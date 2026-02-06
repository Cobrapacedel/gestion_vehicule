import json
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status, generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    CustomUser,
    SimpleProfile,
    BusinessProfile,
    LoginAttempt,
    LoginHistory,
    Client,
    Employee,
)
from .serializers import (
    RegisterSimpleUserSerializer,
    RegisterBusinessUserSerializer,
    SimpleProfileSerializer,
    BusinessProfileSerializer,
    UserSerializer,
    LoginAttemptSerializer,
    LoginHistorySerializer,
    UserSerializer,
    ClientSerializer,
    EmployeeSerializer,
)


class APIEmployeeViewSet(viewsets.ModelViewSet):
    """
    API CRUD pour les employés.
    Accessible selon le rôle de l'utilisateur.
    """
    queryset = Employee.objects.all().order_by("-created_at")
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]  # tu peux adapter selon le rôle

    def get_queryset(self):
        user = self.request.user
        # Admin voit tous les employés
        if user.is_staff:
            return Employee.objects.all().order_by("-created_at")
        # Les utilisateurs liés à un business ne voient que leurs employés
        return Employee.objects.filter(business__user=user).order_by("-created_at")

class APIClientViewSet(viewsets.ModelViewSet):
    """
    API CRUD pour les clients.
    Accessible aux admins et aux utilisateurs authentifiés selon le rôle.
    """
    queryset = Client.objects.all().order_by("-created_at")
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]  # tu peux adapter selon le rôle

    def get_queryset(self):
        user = self.request.user
        # Si l'utilisateur est admin, retourne tous les clients
        if user.is_staff:
            return Client.objects.all().order_by("-created_at")
        # Sinon, retourne seulement les clients liés à cet utilisateur
        return Client.objects.filter(real_user=user).order_by("-created_at")

class APIUserViewSet(viewsets.ModelViewSet):
    """
    API CRUD pour les utilisateurs.
    Accessible seulement aux admins.
    """
    queryset = CustomUser.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
# ==========================
# 🔹 LISTE DES TENTATIVES DE LOGIN
# ==========================
class APILoginAttemptView(generics.ListAPIView):
    """
    Liste les tentatives de connexion pour l'utilisateur connecté.
    Utile pour que l'utilisateur puisse voir ses échecs et verrouillages.
    """
    serializer_class = LoginAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Retourne uniquement les tentatives liées à l'utilisateur courant
        return LoginAttempt.objects.filter(user=self.request.user)

# ==========================
# 🔹 MISE À JOUR PROFIL UTILISATEUR SIMPLE
# ==========================
class APISimpleProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = SimpleProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retourne le profil lié à l'utilisateur connecté
        return self.request.user.profile

# ==========================
# 🔹 MISE À JOUR PROFIL BUSINESS
# ==========================
class APIBusinessProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Retourne le profil business lié à l'utilisateur connecté
        return self.request.user.business_profile
        
# =============================================================
# 🔹 UTILITAIRES
# =============================================================

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request):
    return request.META.get("HTTP_USER_AGENT", "Unknown device")


def generate_tokens(user):
    """Retourne un token JWT complet (refresh + access)."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# =============================================================
# 🔹 INSCRIPTION UTILISATEUR SIMPLE
# =============================================================
class APIRegisterSimpleUserView(generics.CreateAPIView):
    serializer_class = RegisterSimpleUserSerializer
    permission_classes = [permissions.AllowAny]


# =============================================================
# 🔹 INSCRIPTION UTILISATEUR BUSINESS
# =============================================================
class APIRegisterBusinessUserView(generics.CreateAPIView):
    serializer_class = RegisterBusinessUserSerializer
    permission_classes = [permissions.AllowAny]


# =============================================================
# 🔹 CONNEXION (AVEC LOGIN ATTEMPTS + HISTORY)
# =============================================================
class APILoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        ip = get_client_ip(request)
        agent = get_user_agent(request)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Identifiants incorrects."}, status=401)

        # Tentatives
        attempt, created = LoginAttempt.objects.get_or_create(user=user)

        # Si verrouillé
        if attempt.is_locked():
            remaining = (attempt.locked_until - timezone.now()).seconds
            return Response(
                {"detail": f"Compte bloqué temporairement ({remaining} sec)."},
                status=429
            )

        authenticated = authenticate(email=email, password=password)

        if authenticated is None:
            attempt.register_failed_attempt()
            return Response({"detail": "Identifiants incorrects."}, status=401)

        # Reset tentative après succès
        attempt.reset_attempts()

        # Historique
        LoginHistory.log_login(authenticated, ip_address=ip, user_agent=agent)

        # Tokens JWT
        tokens = generate_tokens(authenticated)

        return Response({
            "message": "Connexion réussie",
            "tokens": tokens,
            "user": UserSerializer(authenticated).data
        })


# =============================================================
# 🔹 DECONNEXION JWT (Blacklist)
# =============================================================
class APILogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
        except Exception:
            pass
        return Response({"message": "Déconnexion réussie"})


# =============================================================
# 🔹 PROFIL UTILISATEUR SIMPLE (GET / PATCH)
# =============================================================
class APISimpleProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SimpleProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.simple_profile


# =============================================================
# 🔹 PROFIL BUSINESS (GET / PATCH)
# =============================================================
class APIBusinessProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.business_profile


# =============================================================
# 🔹 HISTORIQUE DES CONNEXIONS
# =============================================================
class APILoginHistoryView(generics.ListAPIView):
    serializer_class = LoginHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user)


# =============================================================
# 🔹 LISTE DES UTILISATEURS (pour admin ou business manager)
# =============================================================
class APIUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return CustomUser.objects.all().order_by("-created_at")


# =============================================================
# 🔹 VERIFIER EMAIL & TELEPHONE (AJAX)
# =============================================================
class APICheckEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.GET.get("email")
        exists = CustomUser.objects.filter(email=email).exists()
        return Response({"email_exists": exists})


class APICheckPhoneView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        phone = request.GET.get("phone")
        exists = CustomUser.objects.filter(phone=phone).exists()
        return Response({"phone_exists": exists})


# =============================================================
# 🔹 PROMOUVOIR UN CLIENT → VRAI UTILISATEUR
# =============================================================
class APIClientPromoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({"detail": "Client introuvable"}, status=404)

        email = request.data.get("email")
        password = request.data.get("password") or None

        new_user = client.promote(email=email, password=password)

        return Response({
            "message": "Client promu en utilisateur réel",
            "user": UserSerializer(new_user).data
        })
        
# =============================================================
# 🔹 EMPLOYEE
# =============================================================
class APIEmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by("email")
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # un business voit uniquement ses employés
        if user.user_type == "business":
            return Employee.objects.filter(business=user.businessprofile)
        return Employee.objects.none()

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.businessprofile)

# 🔹 Détail + update + delete
class APIEmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "business":
            return Employee.objects.filter(business=user.businessprofile)
        return Employee.objects.none()