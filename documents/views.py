from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils.translation import gettext as _
from django.urls import reverse
from .models import Document, DocumentRenewal
from .forms import (
    DocumentForm,
    DocumentRenewalForm,
)
from vehicles.models import Vehicle
from payments.models import Payment


# -----------------------------
# Document CRUD
# -----------------------------
@login_required
def document_list(request):
    qs = Document.objects.filter(user=request.user)
    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "documents/document_list.html",
        {"page_obj": page_obj, "total": qs.count()},
    )


@login_required
def document_create(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            messages.success(request, _("Document créé avec succès."))
            return redirect("documents:document_detail", pk=doc.pk)
    else:
        form = DocumentForm()
    return render(request, "documents/document_form.html", {"form": form})


@login_required
def document_detail(request, pk):
    doc = get_object_or_404(Document, pk=pk, user=request.user)
    renewals = doc.renewals.all()[:5]
    payments = doc.payments.all()[:5]
    return render(
        request,
        "documents/document_detail.html",
        {"document": doc, "renewals": renewals, "payments": payments},
    )


@login_required
def document_update(request, pk):
    doc = get_object_or_404(Document, pk=pk, user=request.user)
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            messages.success(request, _("Document mis à jour."))
            return redirect("documents:document_detail", pk=doc.pk)
    else:
        form = DocumentForm(instance=doc)
    return render(request, "documents/document_form.html", {"form": form})


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk, user=request.user)
    if request.method == "POST":
        doc.delete()
        messages.success(request, _("Document supprimé."))
        return redirect("documents:document_list")
    return render(request, "documents/document_confirm_delete.html", {"document": doc})


# -----------------------------
# Renouvellement
# -----------------------------
@login_required
def renewal_create(request, doc_pk):
    doc = get_object_or_404(Document, pk=doc_pk, user=request.user)
    if request.method == "POST":
        form = DocumentRenewalForm(request.POST)
        if form.is_valid():
            renewal = form.save(commit=False)
            renewal.document = doc
            renewal.save()
            messages.success(request, _("Renouvellement enregistré."))
            return redirect("documents:document_detail", pk=doc.pk)
    else:
        form = DocumentRenewalForm(initial={"document": doc})
    return render(
        request,
        "documents/renewal_form.html",
        {"form": form, "document": doc},
    )


# -----------------------------
# Paiement
# -----------------------------
from payments.services.payment_service import PaymentService
from django.core.exceptions import ValidationError

@login_required
def document_pay(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if not user_can_access_document(request.user, document):
        messages.error(request, "Accès refusé.")
        return redirect("documents:document_list")

    if document.is_paid:
        messages.info(request, "Ce document est déjà payé.")
        return redirect("payments:payment_list")

    if request.method == "POST":
        try:
            PaymentService.document_pay(
                user=request.user,
                document=document
            )
            messages.success(request, "Document payé avec succès.")
            return redirect("payments:payment_list")

        except ValidationError as e:
            messages.error(request, str(e))

    return render(
        request,
        "documents/document_payment_form.html",
        {"document": document}
    )