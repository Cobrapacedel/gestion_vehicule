from django.views.generic import ListView, DetailView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from .models import TollBooth
from django.contrib.auth.decorators import login_required
from users.decorators import verified_required
from django.views.generic import DetailView
from .models import TollBooth
from .models import TollDebt
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

class TollDebtListView(ListView):
    model = TollDebt
    template_name = "tolls/toll_debt_list.html"
    context_object_name = "debts"

    def get_queryset(self):
        return TollDebt.objects.filter(user=self.request.user)
    
    


@login_required
def tollbooth_list_view(request):
    tolls = TollBooth.objects.all()
    return render(request, "payments/tollbooth_list.html", {"tolls": tolls})

@login_required
def toll_detail_view(request, toll_id):
    toll = get_object_or_404(TollBooth, id=toll_id)
    return render(request, "payments/tollbooth_detail.html", {"toll": toll})
    
from payments.services.payment_service import PaymentService
from django.core.exceptions import ValidationError


@verified_required
@login_required
def toll_pay(request, toll_id):
    toll = get_object_or_404(Toll, id=toll_id)

    if not user_can_access_fine(request.user, toll):
        messages.error(request, "Accès refusé.")
        return redirect("tolls:toll_list")

    if toll.is_paid:
        messages.info(request, "Ce Péage est déjà payé.")
        return redirect("payments:payment_list")

    if request.method == "POST":
        try:
            PaymentService.toll_pay(
                user=request.user,
                toll=toll
            )
            messages.success(request, "Péage payé avec succès.")
            return redirect("payments:payment_list")

        except ValidationError as e:
            messages.error(request, str(e))

    return render(
        request,
        "tolls/toll_pay_form.html",
        {"toll": toll}
    )


