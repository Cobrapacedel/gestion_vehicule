# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Recharge, Transaction, Payment, Balance, FundTransfer
from .forms import (
    RechargeForm,
    TransactionForm,
    FundTransferForm,
)
from fines.models import Fine
from users.models import CustomUser
from django.shortcuts import render, redirect
from .models import Wallet
from .forms import WalletForm
from .services.blockchain_utils import get_bsc_balance
from .utils import get_bsc_wallet_balance
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import FinePaymentForm, DocumentPaymentForm, TollPaymentForm


def fine_payment_view(request):
    return render(request, 'fines/fine_payment_form.html')

def document_payment_view(request):
    return render(request, 'documents/document_payment_form.html')

def toll_payment_view(request):
    return render(request, 'tolls/toll_payment_form.html')

@login_required
def wallet_detail(request):
    wallet, created = Wallet.objects.get_or_create(
    user=request.user,
    defaults={
        'public_key': '0x0000000000000000000000000000000000000000',  # valeur temporaire
        'network': 'bsc',
        'wallet_balance': 0
    }
)
    if request.method == 'POST':
        form = WalletForm(request.POST, instance=wallet)
        if form.is_valid():
            wallet = form.save()
            try:
                if wallet.network == 'bsc':
                    wallet.wallet_balance = get_bsc_wallet_balance(wallet.public_key)
                    wallet.save()
            except Exception as e:
                form.add_error(None, f"Erreur d'actualisation : {e}")
    else:
        form = WalletForm(instance=wallet)
    return render(request, 'payments/wallet_detail.html', {'form': form, 'wallet': wallet})


# --- AMENDES ---

@login_required
def pay_bill_view(request):
    user = request.user
    fines = Fine.objects.filter(user=user, paid=False).order_by('issued_at')
    balance = Balance.objects.filter(user=user).first()

    if request.method == "POST":
        fine_id = request.POST.get("fine_id")
        fine = get_object_or_404(Fine, id=fine_id, user=user)

        if balance and balance.amount >= fine.amount:
            balance.amount -= fine.amount
            balance.save()

            fine.status = "Paid"
            fine.paid_at = timezone.now()
            fine.save()

            Transaction.objects.create(
                user=user,
                amount=fine.amount,
                payment_method="solde",
                status="Complété",
                description=f"Règleman amann #{fine.id}",
            )

            messages.success(request, f"Ou peye amann #{fine.id} avèk siksè.")
            return redirect("payments:pay_bill")
        else:
            messages.error(request, "Ou pa gen ase lajan sou kont ou pou peye amann sa.")

    return render(request, "payments/pay_bill.html", {"fines": fines, "balance": balance})


# --- PAIEMENTS (CBV) ---

class PaymentListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = "payments/payment_list.html"
    context_object_name = "payments"

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = "payments/payment_detail.html"
    context_object_name = "payment"

    def get_object(self):
        return get_object_or_404(Payment, pk=self.kwargs["pk"], user=self.request.user)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    template_name = "payments/payment_form.html"
    fields = ["amount", "currency", "payment_type"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("payments:payment_list")


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    model = Payment
    template_name = "payments/payment_form.html"
    fields = ["amount", "currency", "payment_type"]

    def get_object(self):
        return get_object_or_404(Payment, pk=self.kwargs["pk"], user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("payments:payment_list")


class PaymentDeleteView(LoginRequiredMixin, DeleteView):
    model = Payment
    template_name = "payments/payment_confirm_delete.html"
    context_object_name = "payment"
    success_url = reverse_lazy("payments:payment_list")

    def get_object(self):
        return get_object_or_404(Payment, pk=self.kwargs["pk"], user=self.request.user)


# --- RECHARGES (CBV + HTMX) ---

class RechargeListView(LoginRequiredMixin, ListView):
    model = Recharge
    template_name = "payments/recharges/recharge_list.html"
    context_object_name = "recharges"

    def get_queryset(self):
        return Recharge.objects.filter(user=self.request.user)


class RechargeDetailView(LoginRequiredMixin, DetailView):
    model = Recharge
    template_name = "payments/recharges/recharge_detail.html"
    context_object_name = "recharge"

    def get_object(self):
        return get_object_or_404(Recharge, pk=self.kwargs["pk"], user=self.request.user)


class RechargeCreateView(LoginRequiredMixin, CreateView):
    model = Recharge
    template_name = "payments/recharges/recharge_form.html"
    fields = ["amount", "currency", "method"]

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("payments:recharge_list")


@login_required
def recharge_create_htmx(request):
    if request.method == "POST":
        form = RechargeForm(request.POST)
        if form.is_valid():
            form.save()
            if request.htmx:
                return HttpResponse('<div class="text-green-600 font-bold">Rechaj fèt avèk siksè!</div>')
        elif request.htmx:
            return render(request, "payments/partials/recharge_form.html", {"form": form})
    else:
        form = RechargeForm()
    
    return render(request, "payments/recharges/recharge_create.html", {"form": form})


@login_required
def complete_recharge(request, pk):
    recharge = get_object_or_404(Recharge, pk=pk, user=request.user)
    if recharge.status != "Completed":
        recharge.complete_recharge()
    return redirect("payments:recharge_detail", pk=recharge.pk)


@login_required
def recharge_form(request):
    if request.method == "POST":
        recharge = Recharge.objects.create(
            user=request.user,
            amount=request.POST.get("amount"),
            currency=request.POST.get("currency"),
            method=request.POST.get("method"),
        )
        return JsonResponse({"success": True, "id": recharge.id})
    return render(request, "payments/recharges/recharge_form.html")


# --- TRANSACTIONS ---

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "payments/transactions/transaction_create.html"
    success_url = reverse_lazy("payments:transaction_list")


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "payments/transactions/transaction_delete.html"
    context_object_name = "transaction"
    success_url = reverse_lazy("payments:transaction_list")


@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(transactions, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'payments/transactions/transaction_list.html', {'page_obj': page_obj})


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    return render(request, 'payments/transactions/transaction_detail.html', {'transaction': transaction})


# --- TRANSFERT DE FONDS ---

@login_required
def fund_transfer_create(request):
    if request.method == 'POST':
        form = FundTransferForm(request.POST, sender=request.user)
        if form.is_valid():
            transfer = form.save(commit=False)
            if request.user.balance.amount >= transfer.amount:
                transfer.sender = request.user
                transfer.save()

                # Débit/crédit
                request.user.balance.amount -= transfer.amount
                transfer.recipient.balance.amount += transfer.amount
                request.user.balance.save()
                transfer.recipient.balance.save()

                messages.success(request, "Transfert effectué avec succès.")
                return redirect('payments:fund_transfer_form')
            else:
                form.add_error('amount', "Solde insuffisant.")
    else:
        form = FundTransferForm(sender=request.user)

    return render(request, 'payments/transfers/fund_transfer_form.html', {'form': form})
    
@login_required
def fund_transfer_list(request):
    return render(request, "payments/transfers/fund_transfer_list.html")


@login_required
def fund_transfer_delete(request, pk):
    transfer = get_object_or_404(FundTransfer, pk=pk, sender=request.user)
    if request.method == "POST":
        transfer.delete()
        messages.success(request, "Le transfert a été supprimé avec succès.")
        return redirect("payments:transaction_list")

    return render(request, "payments/transfers/fund_transfert_delete.html", {"transfer": transfer})


# --- FORMULAIRES SPÉCIFIQUES ---

@login_required
def fine_payment_view(request):
    if request.method == 'POST':
        form = FinePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_type = 'fine'
            payment.user = request.user
            payment.save()
            messages.success(request, "Peman pou kontravansyon fèt avèk siksè.")
            return redirect('payments:payment_list')
    else:
        form = FinePaymentForm()
    return render(request, 'payments/fine_payment_form.html', {'form': form})


@login_required
def toll_payment_view(request):
    if request.method == 'POST':
        form = TollPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_type = 'toll'
            payment.user = request.user
            payment.save()
            messages.success(request, "Peman pou peyaj fèt avèk siksè.")
            return redirect('payments:payment_list')
    else:
        form = TollPaymentForm()
    return render(request, 'payments/toll_payment_form.html', {'form': form})


@login_required
def document_payment_view(request):
    if request.method == 'POST':
        form = DocumentPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.payment_type = 'document'
            payment.user = request.user
            payment.save()
            messages.success(request, "Peman dokiman fèt avèk siksè.")
            return redirect('payments:payment_list')
    else:
        form = DocumentPaymentForm()
    return render(request, 'payments/document_payment_form.html', {'form': form})