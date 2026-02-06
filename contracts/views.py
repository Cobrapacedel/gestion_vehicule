from datetime import timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from vehicles.models import Vehicle
from users.models import Employee
from .models import Contract
from .forms import ContractForm

from payments.models import Payment
from payments.services.payment_service import PaymentService
from payments.services.balance_service import BalanceService

User = get_user_model()


# -----------------------------------------------------
#   LISTE DES CONTRATS
# -----------------------------------------------------
@login_required
def contract_list(request):
    contracts = (
        Contract.objects
        .select_related("old_user", "new_user", "vehicle")
        .order_by("-created_at")
    )

    paginator = Paginator(contracts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "contracts/contract_list.html",
        {
            "contracts": page_obj.object_list,
            "page_obj": page_obj,
        },
    )


# -----------------------------------------------------
#   CRÉATION D’UN CONTRAT
# -----------------------------------------------------
@login_required
def contract_create(request):
    if request.method == "POST":
        form = ContractForm(request.POST, user=request.user)

        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user

            # Limite 30 jours pour les prêts
            if contract.contract_type == Contract.CONTRACT_LOAN:
                max_end = contract.start_date + timedelta(days=30)
                if contract.end_date > max_end:
                    messages.error(request, "Durée d’un prêt limitée à 30 jours.")
                    return render(request, "contracts/contract_form.html", {"form": form})

            contract.save()
            messages.success(request, "Contrat créé avec succès.")
            return redirect("contracts:contract_list")

    else:
        form = ContractForm(user=request.user)

    return render(request, "contracts/contract_form.html", {"form": form})


# -----------------------------------------------------
#   MODIFICATION D’UN CONTRAT
# -----------------------------------------------------
@login_required
def contract_update(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    if request.method == "POST":
        form = ContractForm(request.POST, instance=contract, user=request.user)

        if form.is_valid():
            contract = form.save(commit=False)

            if contract.contract_type == Contract.CONTRACT_LOAN:
                max_end = contract.start_date + timedelta(days=30)
                if contract.end_date > max_end:
                    messages.error(request, "Durée d’un prêt limitée à 30 jours.")
                    return render(
                        request,
                        "contracts/contract_form.html",
                        {"form": form, "contract": contract},
                    )

            contract.save()
            messages.success(request, "Contrat modifié avec succès.")
            return redirect("contracts:contract_list")

    else:
        form = ContractForm(instance=contract, user=request.user)

    return render(
        request,
        "contracts/contract_form.html",
        {"form": form, "contract": contract},
    )


# -----------------------------------------------------
#   DÉTAIL D’UN CONTRAT + PAIEMENTS
# -----------------------------------------------------
@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    if request.user not in [contract.old_user, contract.new_user, contract.created_by_owner]:
        messages.error(request, "Accès refusé.")
        return redirect("contracts:contract_list")

    payments = Payment.objects.filter(
        payment_type="contract",
        metadata__contract_id=contract.id
    ).order_by("-created_at")

    context = {
        "contract": contract,
        "payments": payments,
        "total_paid": contract.total_paid,
        "remaining_amount": contract.remaining_amount,
    }

    return render(request, "contracts/contract_detail.html", context)


# -----------------------------------------------------
#   PAIEMENT D’UN CONTRAT (SOLDE INTERNE)
# -----------------------------------------------------
@login_required
def contract_pay(request, pk):
    contract = get_object_or_404(Contract, pk=pk)

    if request.user not in [contract.old_user, contract.new_user]:
        messages.error(request, "Vous n’avez pas le droit de payer ce contrat.")
        return redirect("contracts:contract_detail", pk=pk)

    amount = contract.remaining_amount

    if amount <= 0:
        messages.info(request, "Ce contrat est déjà entièrement payé.")
        return redirect("contracts:contract_detail", pk=pk)

    try:
        # Débit du solde utilisateur
        BalanceService.debit(
            user=request.user,
            amount=amount,
            currency="HTG",
            description="Paiement contrat"
        )

        # Création du paiement
        payment = PaymentService.create_payment(
            user=request.user,
            amount=amount,
            currency="HTG",
            payment_type="contract",
            metadata={"contract_id": contract.id}
        )

        PaymentService.mark_completed(payment)

        messages.success(request, "Paiement effectué avec succès.")

    except Exception as e:
        messages.error(request, str(e))

    return redirect("contracts:contract_detail", pk=pk)


# -----------------------------------------------------
#   SUPPRESSION D’UN CONTRAT
# -----------------------------------------------------
@login_required
def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    contract.delete()
    messages.success(request, "Contrat supprimé avec succès.")
    return redirect("contracts:contract_list")