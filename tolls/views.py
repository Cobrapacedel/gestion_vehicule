from django.views.generic import ListView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from .models import TollTransaction
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from .models import TollPayment
from .forms import TollPaymentForm
from django.views.generic import ListView
from .models import TollBooth
from django.views.generic import DetailView
from .models import TollBooth
from django.views.generic import DetailView
from django.http import Http404
from .models import TollDebt
from django.views.generic import DeleteView
from django.http import Http404
from django.urls import reverse_lazy
from .models import TollDebt

class TollDebtDeleteView(DeleteView):
    model = TollDebt
    template_name = "payments/toll_debt_confirm_delete.html"
    context_object_name = "debt"
    success_url = reverse_lazy("tolls:debt_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Suppression non autorisée.")
        return obj

class TollDebtDetailView(DetailView):
    model = TollDebt
    template_name = "payments/toll_debt_detail.html"
    context_object_name = "debt"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Dette non trouvée.")
        return obj

class TollDetailView(DetailView):
    model = TollBooth
    template_name = "payments/tollbooth_detail.html"
    context_object_name = "booth"

class TollListView(ListView):
    model = TollBooth
    template_name = "payments/tollbooth_list.html"
    context_object_name = "booths"


class TollPaymentListView(LoginRequiredMixin, ListView):
    model = TollPayment
    template_name = 'tolls/toll_payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10

    def get_queryset(self):
        return TollPayment.objects.filter(user=self.request.user).order_by('-created_at')


class TollPaymentDetailView(LoginRequiredMixin, DetailView):
    model = TollPayment
    template_name = 'tolls/toll_payment_detail.html'
    context_object_name = 'payment'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Pèman pa disponib.")
        return obj


class TollPaymentCreateView(LoginRequiredMixin, CreateView):
    model = TollPayment
    form_class = TollPaymentForm
    template_name = 'tolls/toll_payment_form.html'
    success_url = reverse_lazy('payments:payment_list')

    def form_valid(self, form):
        # Lier le paiement à l'utilisateur connecté
        form.instance.user = self.request.user
        return super().form_valid(form)


class TollPaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = TollPayment
    template_name = 'payments/tollpayment_confirm_delete.html'
    success_url = reverse_lazy('payments:payment_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Suppression non autorisée.")
        return obj


class TollTransactionListView(LoginRequiredMixin, ListView):
    model = TollTransaction
    template_name = 'payments/tolltransaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10

    def get_queryset(self):
        # Retourne uniquement les transactions li��es aux paiements de l'utilisateur connect��
        return TollTransaction.objects.filter(toll_payment__user=self.request.user).order_by('-created_at')


class TollTransactionDetailView(LoginRequiredMixin, DetailView):
    model = TollTransaction
    template_name = 'payments/tolltransaction_detail.html'
    context_object_name = 'transaction'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # V��rifie que la transaction appartient �� l'utilisateur connect��
        if obj.toll_payment.user != self.request.user:
            raise Http404("Transaction non trouv��e.")
        return obj


class TollTransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = TollTransaction
    template_name = 'payments/tolltransaction_confirm_delete.html'
    context_object_name = 'transaction'
    success_url = reverse_lazy('payments:transaction_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # V��rifie que la transaction appartient �� l'utilisateur connect��
        if obj.toll_payment.user != self.request.user:
            raise Http404("Acc��s interdit.")
        return obj
        
# views.py
from django.views import View
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from decimal import Decimal
from django.utils import timezone
from .models import TollPayment, TollTransaction, TollDebt, TollBooth, TollDetection
from vehicles.models import Vehicle
from payments.models import Balance
from users.models import CustomUser


class ProcessTollDetectionView(View):
    def post(self, request):
        plate_number = request.POST.get("plate_number")
        booth_id = request.POST.get("booth_id")

        if not plate_number or not booth_id:
            return JsonResponse({"error": "Invalid data"}, status=400)

        try:
            vehicle = Vehicle.objects.get(plate_number=plate_number)
            user = vehicle.owner
            balance = Balance.objects.get(user=user)
            toll_booth = TollBooth.objects.get(id=booth_id)

            toll_amount = Decimal("1000.00")
            deducted = toll_amount * Decimal("0.80")
            commission = toll_amount * Decimal("0.20")

            if balance.amount >= toll_amount:
                # Paiement automatique
                balance.amount -= deducted
                balance.save()

                payment = TollPayment.objects.create(
                    user=user,
                    toll_booth=toll_booth,
                    amount=toll_amount,
                    status="success"
                )

                TollTransaction.objects.create(
                    toll_payment=payment,
                    reference=get_random_string(12).upper(),
                    status="success"
                )

                # Créer commission en dette
                TollDebt.objects.create(
                    user=user,
                    amount_due=commission,
                    remaining_commission=commission
                )

                return JsonResponse({"message": "Paiement automatique effectué avec succès."})

            else:
                # Solde insuffisant → dette
                TollDebt.objects.create(
                    user=user,
                    amount_due=toll_amount,
                    remaining_commission=commission
                )

                return JsonResponse({"message": "Solde insuffisant. Dette enregistrée."})

        except Vehicle.DoesNotExist:
            return JsonResponse({"error": "Véhicule introuvable"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
from django.views.generic import ListView
from .models import TollDebt

class TollDebtListView(ListView):
    model = TollDebt
    template_name = "payments/toll_debt_list.html"
    context_object_name = "debts"

    def get_queryset(self):
        return TollDebt.objects.filter(user=self.request.user)