from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from payments.models import Payment, Transaction


class PaymentService:
    """
    Service centralisé de gestion des paiements.
    Toutes les applications (fines, contracts, documents, etc.)
    passent obligatoirement par ce service.
    """

    # =====================================================
    # CRÉATION DU PAIEMENT
    # =====================================================
    @staticmethod
    @db_transaction.atomic
    def create_payment(*, user, amount, currency, payment_type, metadata=None):
        """
        Crée un paiement en statut 'pending'.

        Exemples de metadata :
        {
            "fine_id": 12
        }
        {
            "contract_id": 5
        }
        """

        if amount <= 0:
            raise ValidationError("Le montant doit être supérieur à 0")

        payment = Payment.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            payment_type=payment_type,
            status=Payment.STATUS_PENDING,
            metadata=metadata or {},
        )

        return payment

    # =====================================================
    # TRANSACTION TECHNIQUE
    # =====================================================
    @staticmethod
    @db_transaction.atomic
    def attach_transaction(payment: Payment, *, provider=None, reference_id=None, raw_response=None):
        """
        Lie une transaction technique (mobile money, banque, crypto).
        """

        if payment.transaction:
            raise ValidationError("Ce paiement possède déjà une transaction")

        transaction = Transaction.objects.create(
            user=payment.user,
            amount=payment.amount,
            currency=payment.currency,
            status=Transaction.STATUS_PENDING,
            provider=provider,
            reference_id=reference_id,
            raw_response=raw_response,
            description=f"Paiement {payment.payment_type}",
        )

        payment.transaction = transaction
        payment.save(update_fields=["transaction"])

        return transaction

    # =====================================================
    # STATUTS
    # =====================================================
    @staticmethod
    @db_transaction.atomic
    def mark_completed(payment: Payment):
        """
        Marque le paiement comme complété et déclenche la logique métier.
        """

        if payment.status == Payment.STATUS_COMPLETED:
            return payment

        payment.status = Payment.STATUS_COMPLETED
        payment.payment_date = timezone.now()
        payment.save(update_fields=["status", "payment_date"])

        if payment.transaction:
            payment.transaction.status = Transaction.STATUS_COMPLETED
            payment.transaction.save(update_fields=["status"])

        PaymentService._apply_business_effect(payment)
        return payment

    @staticmethod
    @db_transaction.atomic
    def mark_failed(payment: Payment, reason=None):
        """
        Marque le paiement comme échoué.
        """

        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=["status"])

        if payment.transaction:
            payment.transaction.status = Transaction.STATUS_FAILED
            payment.transaction.description = reason
            payment.transaction.save(update_fields=["status", "description"])

        return payment

    @staticmethod
    @db_transaction.atomic
    def refund(payment: Payment):
        """
        Rembourse un paiement complété.
        """

        if payment.status != Payment.STATUS_COMPLETED:
            raise ValidationError("Seuls les paiements complétés peuvent être remboursés")

        payment.status = Payment.STATUS_REFUNDED
        payment.save(update_fields=["status"])

        PaymentService._rollback_business_effect(payment)
        return payment

    # =====================================================
    # DISPATCH MÉTIER
    # =====================================================
    @staticmethod
    def _apply_business_effect(payment: Payment):
        handlers = {
            Payment.TYPE_FINE: PaymentService._handle_fine_payment,
            Payment.TYPE_TOLL: PaymentService._handle_toll_payment,
            Payment.TYPE_RENEWAL: PaymentService._handle_renewal_payment,
            Payment.TYPE_CONTRACT: PaymentService._handle_contract_payment,
        }

        handler = handlers.get(payment.payment_type)
        if handler:
            handler(payment)

    @staticmethod
    def _rollback_business_effect(payment: Payment):
        """
        À implémenter si remboursement avec effet inverse.
        """
        pass

    # =====================================================
    # HANDLERS MÉTIER
    # =====================================================
    @staticmethod
    @db_transaction.atomic
    def _handle_fine_payment(payment: Payment):
        from fines.models import Fine

        fine_id = payment.metadata.get("fine_id")
        if not fine_id:
            return

        fine = (
            Fine.objects
            .select_for_update()
            .filter(id=fine_id, is_paid=False)
            .first()
        )
        if not fine:
            return

        fine.is_paid = True
        fine.paid_at = timezone.now()
        fine.save(update_fields=["is_paid", "paid_at"])

    @staticmethod
    @db_transaction.atomic
    def _handle_renewal_payment(payment: Payment):
        from documents.models import DocumentRenewal

        renewal_id = payment.metadata.get("renewal_id")
        if not renewal_id:
            return

        renewal = (
            DocumentRenewal.objects
            .select_for_update()
            .filter(id=renewal_id)
            .first()
        )
        if not renewal:
            return

        renewal.status = DocumentRenewal.STATUS_PAID
        renewal.save(update_fields=["status"])

    @staticmethod
    @db_transaction.atomic
    def _handle_contract_payment(payment: Payment):
        from contracts.models import Contract

        contract_id = payment.metadata.get("contract_id")
        if not contract_id:
            return

        contract = (
            Contract.objects
            .select_for_update()
            .filter(id=contract_id)
            .first()
        )
        if not contract:
            return

        contract.update_payment_status()
        
    @staticmethod
    @db_transaction.atomic
    def _handle_toll_payment(payment: Payment):
        from tolls.models import Toll

        toll_id = payment.metadata.get("toll_id")
        if not toll_id:
            return

        toll = (
            TOLL.objects
            .select_for_update()
            .filter(id=toll_id)
            .first()
        )
        if not toll:
            return

        toll.update_payment_status()