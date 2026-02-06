from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_POST
from .utils import can_access_client
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import (
    CustomUserCreationForm,
    BusinessProfileForm,
    EmployeeForm,
    ClientForm,
    SimpleProfileForm
)
from .models import Client, SimpleProfile, CustomUser, BusinessProfile, Employee

User = get_user_model()


# ----------------------------
# Helpers
# ----------------------------
def is_admin(user):
    return user.is_staff or user.is_superuser

# ==========================================
#  Inscription utilisateur simple
# ==========================================
def register_user(request):
    user_type = "simple"

    ref_code = request.GET.get("ref") or request.session.get("referral_code")
    referrer = None
    if ref_code:
        referrer = CustomUser.objects.filter(invitation_code=ref_code).first()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, user_type=user_type)
        if form.is_valid():
            user = form.save(commit=False)
            if referrer:
                user.referred_by = referrer
            user.save()

            messages.success(request, "Kont ou kreye avèk siksè.")
            return redirect("login")
    else:
        form = CustomUserCreationForm(user_type=user_type)

    return render(request, "users/register_user.html", {"form": form})

# ----------------------------
# Inscription - Business (dealer / agency / garage)
# ----------------------------
def register_business(request):
    user_type = "business"

    ref_code = request.GET.get("ref") or request.session.get("referral_code")
    referrer = None
    if ref_code:
        referrer = CustomUser.objects.filter(invitation_code=ref_code).first()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, user_type=user_type)
        if form.is_valid():
            user = form.save(commit=False)
            if referrer:
                user.referred_by = referrer
            user.save()

            messages.success(request, "Kont biznis lan kreye avèk siksè.")
            return redirect("login")
    else:
        form = CustomUserCreationForm(user_type=user_type)

    return render(request, "users/register_business.html", {"form": form})

# -------------------------------
# Inscription : choix user / business
# -------------------------------
def register_choice(request):
    return render(request, "users/register_choice.html")
    
# ----------------------------
# Login / Logout (HTML)
# ----------------------------
def login_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect("core:dashboard_redirect")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/login.html", {"form": form})

@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "Déconnecté.")
    return redirect("login")


# ----------------------------
# Profil utilisateur - affichage & édition
# ----------------------------
@login_required
def simple_profile_create(request):
    # Si un profil existe, on redirige vers la page de détail
    if hasattr(request.user, "simple"):
        return redirect("users:simple_profile_detail")

    form = SimpleProfileForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        simple = form.save(commit=False)
        simple.user = request.user
        simple.save()
        messages.success(request, "Profil Itilizatè Senp lan kreye avèk siksè.")
        return redirect("users:simple_profile_detail")

    return render(
        request,
        "users/simples/simple_profile_create.html",
        {"form": form}
    )
    
@login_required
def simple_profile_detail(request):
    simple = SimpleProfile.objects.filter(user=request.user).first()
    
    if simple is None:
        return redirect("users:simple_profile_create")
        
    """Affiche le profil (page dashboard simple)."""
    simple = getattr(request.user, "simple", None)
    return render(request, "users/simples/simple_profile_detail.html", {"simple": simple, "user": request.user})

@login_required
def simple_profile_update(request):
    user = request.user

    # Récupérer le profil simple lié à l'utilisateur
    try:
        simple = user.simple  # related_name="simple"
    except SimpleProfile.DoesNotExist:
        messages.error(request, "Ou poko genyen pwofil senp.")
        return redirect("users:simple_profile_create")

    if request.method == "POST":
        form = SimpleProfileForm(request.POST, request.FILES, instance=simple)

        if form.is_valid():

            # Vérifier si le nom/prénom ont changé
            first_name_new = form.cleaned_data.get("first_name")
            last_name_new = form.cleaned_data.get("last_name")

            if simple.first_name != first_name_new or simple.last_name != last_name_new:
                messages.info(request, "Nou fè mizajou nan non an.")

            form.save()
            messages.success(request, "Pwofil ou chanje avèk siksè.")
            return redirect("users:simple_profile_detail")
        else:
            messages.error(request, "Gen erè nan fòmilè a.")
    else:
        form = SimpleProfileForm(instance=simple)

    return render(request, "users/simples/simple_profile_update.html", {"form": form})

    
@login_required
def simple_profile_delete(request):
    simple = getattr(request.user, "simple", None)

    if not simple:
        messages.error(request, "Ou pa gen pwofil pou efase.")
        return redirect("users:simple_profile_detail")

    if request.method == "POST":
        simple.delete()
        messages.success(request, "Pwofil itilizatè a efase avèk siksè.")
        return redirect("users:simple_profile_detail")

    return render(
        request,
        "users/simples/simple_profile_delete.html",
        {"simple": simple}
    )

# ----------------------------
# Profil business - affichage & édition
# ----------------------------
@login_required
def business_profile_create(request):
    # Si un BusinessProfile existe déjà
    if hasattr(request.user, "businessprofile"):
        return redirect("users:business_profile_detail")

    form = BusinessProfileForm(
        request.POST or None,
        request.FILES or None,
        user=request.user
    )

    if form.is_valid():
        businessprofile = form.save()
        messages.success(request, "Profil Biznis la kreye avèk siksè.")
        return redirect("users:business_profile_detail")

    return render(
        request,
        "users/businesses/business_profile_create.html",
        {"form": form}
    )
    
@login_required
def business_profile_detail(request):
    # Vérification : doit être un utilisateur business
    if request.user.user_type != "business":
        messages.error(request, "Accès refusé.")
        return redirect("core:dashboard_redirect")

    businessprofile = getattr(request.user, "businessprofile", None)

    # Si pas de profil → création obligatoire
    if not businessprofile:
        return redirect("users:business_profile_create")

    return render(
        request,
        "users/businesses/business_profile_detail.html",
        {"businessprofile": businessprofile}
    )
    
@login_required
def business_profile_update(request):

    if request.user.user_type != "business":
        messages.error(request, "Accès refusé.")
        return redirect("core:dashboard_redirect")

    businessprofile = getattr(request.user, "businessprofile", None)

    if not businessprofile:
        return redirect("users:business_profile_create")

    if request.method == "POST":
        form = BusinessProfileForm(
            request.POST,
            request.FILES or None,
            instance=businessprofile,
            user=request.user
        )
        if form.is_valid():
            form.save()

            # Mise à jour email + téléphone du User
            request.user.email = form.cleaned_data.get("email", request.user.email)
            request.user.phone = form.cleaned_data.get("phone", request.user.phone)
            request.user.save()

            messages.success(request, "Mizajou fèt avèk siksè.")
            return redirect("users:business_profile_detail")

        messages.error(request, "Gen erè nan fòm nan. Tanpri korije yo.")
    else:
        form = BusinessProfileForm(instance=businessprofile, user=request.user)

    return render(
        request,
        "users/businesses/business_profile_update.html",
        {"form": form}
    )
    
@login_required
def business_profile_delete(request):

    if request.user.user_type != "business":
        messages.error(request, "Aksè entèdi.")
        return redirect("core:dashboard_redirect")

    businessprofile = getattr(request.user, "businessprofile", None)

    if not businessprofile:
        messages.error(request, "Ou pa gen pwofil pou efase.")
        return redirect("users:business_profile_detail")

    if request.method == "POST":
        businessprofile.delete()
        messages.success(request, "Pwofil biznis la efase avèk siksè.")
        return redirect("core:dashboard_redirect")

    return render(
        request,
        "users/businesses/business_profile_delete.html",
        {"business": business}
    )

# ----------------------------
# Lien d'Invitation
# ----------------------------    
def invitation_redirect(request, code):
    inviter = get_object_or_404(User, invitation_code=code)

    if request.user.is_authenticated and request.user == inviter:
        messages.warning(request, "Ou pa ka envite tèt ou.")
        return redirect("core:dashboard_redirect")

    request.session["referral_code"] = inviter.invitation_code
    request.session.set_expiry(60 * 60 * 24)

    return redirect("users:register_choice")
    
# ----------------------------
# Liste utilisateurs (pour admin)
# ----------------------------
@user_passes_test(is_admin)
def user_list(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.all().order_by("-created_at")
    if q:
        qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
    paginator_page = request.GET.get("page", 1)
    # Simple pagination si tu veux remplacer par Paginator dans ton code
    return render(request, "users/user_list.html", {"users": qs})


# ----------------------------
# Détails utilisateur
# ----------------------------
@login_required
def user_detail(request, pk):
    u = get_object_or_404(User, pk=pk)
    # autorisations : admin ou la personne elle-même
    if request.user != u and not is_admin(request.user):
        messages.error(request, "Accès refusé.")
        return redirect("core:dashboard_redirect")
    return render(request, "users/user_detail.html", {"user_obj": u})


# ----------------------------
# Promotion d'un client anonyme en CustomUser (action HTML)
# ----------------------------
@login_required
def promote_client_view(request, pk):
    """
    Page + action pour promouvoir un client 'Client' en utilisateur.
    Utilise la méthode Client.promote().
    """
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password") or None
        new_user = client.promote(email=email, password=password)
        messages.success(request, f"Client promu en utilisateur : {new_user.get_full_name()}")
        return redirect("users:user_detail", pk=new_user.pk)
    return render(request, "users/client_promote.html", {"client": client})

# ----------------------------
# Gestion d'un employé  anonyme en CustomUser (action HTML)
# ---------------------------
@login_required
def employee_list(request):
    q = request.GET.get("q", "").strip()

    qs = (
        Employee.objects
        .select_related("business", "user")
        .order_by("first_name")
    )

    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(employee_type__icontains=q) |
            Q(position__icontains=q) |
            Q(business__business_name__icontains=q)
        )

       # Pagination
    paginator = Paginator(qs, 15)  # 15 clients par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "users/employees/employee_list.html", {"page_obj": page_obj, "q": q})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    # Vérification des droits d'accès
    is_business_owner = hasattr(employee, "business_user") and employee.business_user == request.user
    is_employee_itself = hasattr(employee, "user") and employee.user == request.user
    is_superuser = request.user.is_superuser

    if not (is_business_owner or is_employee_itself or is_superuser):
        messages.error(request, "Ou pa gen otorizasyon pou w gade enfòmasyon sa yo.")
        return redirect("users:employee_list")

    return render(
        request,
        "users/employees/employee_detail.html",
        {"employee": employee}
    )

@login_required
def employee_create(request):

    # Vérifier si l'utilisateur a un business
    business = BusinessProfile.objects.filter(user=request.user).first()

    if business is None:
        # Rediriger vers création ou modification du business
        messages.warning(request, "Ou dwe kreye pwofil antrepriz ou avan ou ka ajoute anplwaye.")
        return redirect("users:profile_business_update")

    # Formulaire normal
    if request.method == "POST":
        form = EmployeeForm(request.POST, business_user=request.user)

        if form.is_valid():
            employee = form.save(commit=False)
            employee.business = business
            employee.save()
            messages.success(request, "Anplwaye kreye avèk siksè ✓")
            return redirect("users:employee_list")

    else:
        form = EmployeeForm(business_user=request.user)

    return render(request, "users/employees/employee_form.html", {"form": form})

@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee, business_user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Anplwaye modifye avèk siksè ✔")
            return redirect("users:employee_detail", pk=pk)
    else:
        form = EmployeeForm(instance=employee, business_user=request.user)

    return render(request, "users/employees/employee_form.html", {"form": form})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        employee.delete()
        messages.success(request, "Anplwaye efase avèk siksè ❌")
        return redirect("users:employee_list")

    return render(request, "users/employees/employee_delete.html", {"employee": employee})
    
# ----------------------------
# Gestion d'un client  anonyme en CustomUser (action HTML)
# ----------------------------
@login_required
def client_list(request):
    q = request.GET.get("q")

    qs = (
        Client.objects
        .visible_for(request.user)
        .select_related("created_by", "real_user")
        .order_by("email")
    )

    if q:
        q = q.strip()
        if q:
            qs = qs.filter(
                Q(real_user__simple__first_name__icontains=q) |
                Q(real_user__simple__last_name__icontains=q) |
                Q(real_user__email__icontains=q) |
                Q(real_user__phone__icontains=q) |
                Q(real_user__simple__address__icontains=q) |
                Q(real_user__businessprofile__business_name__icontains=q)
            )

    paginator = Paginator(qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "users/clients/client_list.html",
        {
            "page_obj": page_obj,
            "q": q,
        }
    )
    
@login_required
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST, request_user=request.user)
        if form.is_valid():
            cli = form.save(commit=False)
            cli.owner = request.user          # ✅ CRITIQUE
            cli.created_by = request.user
            cli.save()
            messages.success(request, "Client créé avec succès ✅")
            return redirect("users:client_list")
    else:
        form = ClientForm(request_user=request.user)

    return render(request, "users/clients/client_form.html", {"form": form})
    
@login_required
def client_detail(request, pk):
    client = get_object_or_404(
        Client.objects.visible_for(request.user),
        pk=pk
    )

    return render(
        request,
        "users/clients/client_detail.html",
        {"client": client}
    )
    
@login_required
def client_update(request, pk):
    cli = get_object_or_404(
        Client.objects.visible_for(request.user),
        pk=pk
    )

    if request.method == "POST":
        form = ClientForm(request.POST, instance=cli)
        if form.is_valid():
            form.save()
            messages.success(request, "Client mis à jour ✅")
            return redirect("users:client_detail", pk=cli.pk)
    else:
        form = ClientForm(instance=cli)

    return render(request, "users/clients/client_form.html", {"form": form})
    
@login_required
def client_delete(request, pk):
    client = get_object_or_404(
        Client.objects.visible_for(request.user),
        pk=pk
    )

    if request.method == "POST":
        client.delete()
        messages.success(request, "Kliyan efase avèk siksè ❌")
        return redirect("users:client_list")

    return render(
        request,
        "users/clients/client_delete.html",
        {"client": client}
    )
    
# ----------------------------
# HTMX: Recherche bénéficiaire (users + clients externes)
# ----------------------------
@login_required
def search_beneficiary(request):
    """
    Requête HTMX (GET) :
    - paramètre 'q' : texte recherché (nom / prénom / email / phone / driver_license)
    Retourne partial template with matching users and clients.
    """
    q = request.GET.get("q", "").strip()
    context = {"query": q, "create_new": False, "results": {"users": [], "clients": []}}
    if not q:
        return render(request, "users/beneficiary_results.html", context)

    # Cherche utilisateurs enregistrés (limite 10)
    users_qs = User.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q) | Q(driver_license__icontains=q)
    ).exclude(id=request.user.id)[:10]

    # Cherche clients externes
    clients_qs = Client.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(phone__icontains=q) | Q(driver_license__icontains=q) | Q(email__icontains=q)
    )[:10]

    if not users_qs.exists() and not clients_qs.exists():
        context["create_new"] = True
        context["results"] = {"users": [], "clients": []}
    else:
        context["results"] = {"users": users_qs, "clients": clients_qs}
    return render(request, "users/beneficiary_results.html", context)


# ----------------------------
# HTMX: Créer client temporaire (POST) — utilisé si aucun utilisateur trouvé
# ----------------------------
@login_required
@require_POST
def create_temp_client(request):
    """
    Attendu (form HTMX) : first_name, last_name, phone, driver_license, email (optionnel)
    Crée un Client lié au user (created_by) et renvoie fragment HTMX mettant à jour le formulaire.
    """
    first_name = request.POST.get("first_name", "").strip()
    last_name = request.POST.get("last_name", "").strip()
    phone = request.POST.get("phone", "").strip()
    driver_license = request.POST.get("driver_license", "").strip()
    email = request.POST.get("email", "").strip()

    if not first_name or not last_name:
        return HttpResponseBadRequest("Prénom et nom requis.")

    client = Client.objects.create(
        first_name=first_name,
        last_name=last_name,
        phone=phone or "",
        email=email or "",
        created_by=request.user,
    )

    # Retourne un petit fragment HTMX confirmant la création et transmet l'id
    return render(request, "users/beneficiary_created.html", {"client": client})


# ----------------------------
# Endpoint HTMX pour fixer le bénéficiaire dans le formulaire de prêt
# (ce endpoint accepte POST hx-vals et renvoie fragment confirmant la sélection)
# ----------------------------
@login_required
@require_POST
def set_beneficiary(request):
    btype = request.POST.get("beneficiary_type")
    bid = request.POST.get("beneficiary_id")
    if not btype or not bid:
        return HttpResponseBadRequest("Paramètres manquants.")
    if btype == "user":
        beneficiary = get_object_or_404(User, pk=bid)
        label = beneficiary.get_full_name()
        payload = {"type": "user", "id": beneficiary.id, "label": label}
    else:
        client = get_object_or_404(Client, pk=bid)
        label = client.get_display_name()
        payload = {"type": "client", "id": client.id, "label": label}

    # Renvoie un fragment qui remplacera la zone de résultats HTMX (bouton/surbrillance)
    return render(request, "users/beneficiary_selected.html", payload)
    
@login_required
def toggle_email_notifications(request):
    profile = request.user.profile
    profile.email_notifications = not profile.email_notifications
    profile.save(update_fields=["email_notifications"])

    # Si la requête vient d’AJAX → retourne JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"email_notifications": profile.email_notifications})

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def toggle_sms_notifications(request):
    profile = request.user.profile
    profile.sms_notifications = not profile.sms_notifications
    profile.save(update_fields=["sms_notifications"])

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"sms_notifications": profile.sms_notifications})

    return redirect(request.META.get("HTTP_REFERER", "/"))