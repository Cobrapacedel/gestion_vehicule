import secrets
import phonenumbers
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
import requests

# Utility Functions

def can_access_client(user, client):
    return client.real_user == user or user.is_superuser or is_admin(user)

def is_admin(user):
    """
    Vérifie si l'utilisateur est administrateur pour ton projet.
    Un administrateur est soit :
      - superuser Django
      - ou un utilisateur avec role 'admin', 'dealer', 'agency' ou 'garage'
    """

    if not user or user.is_anonymous:
        return False

    # Définition des rôles considérés comme administrateurs
    admin_roles = {"admin", "dealer", "agency", "garage"}

    return user.is_superuser or (getattr(user, "role", None) in admin_roles)

def generate_otp(length=6):
    """
    Génère un OTP sécurisé aléatoire.
    :param length: Longueur de l'OTP (par défaut 6 chiffres).
    :return: Une chaîne de caractères contenant l'OTP.
    """
    return str(secrets.randbelow(10**length)).zfill(length)  # Toujours `length` chiffres

def validate_phone(phone):
    """
    Valide un numéro de téléphone avec la bibliothèque `phonenumbers`.
    :param phone: Numéro de téléphone à valider.
    :raises ValidationError: Si le numéro est invalide.
    """
    try:
        parsed = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError("Numéro de téléphone invalide.")
    except phonenumbers.NumberParseException:
        raise ValidationError("Format de numéro de téléphone incorrect.")

def send_email_safe(
    *,
    user=None,
    to_email=None,
    subject="",
    message="",
    fail_silently=True,
):
    """
    Envoi d'email sécurisé.
    Accepte soit un user, soit une adresse email directe.
    """

    recipient = None

    if user and getattr(user, "email", None):
        recipient = user.email
    elif to_email:
        recipient = to_email

    if not recipient:
        logger.warning("Email non envoyé (aucun destinataire) : %s", subject)
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=fail_silently,
        )
        return True
    except Exception as e:
        logger.exception("Erreur lors de l'envoi email : %s", e)
        if not fail_silently:
            raise
        return False

def send_otp_via_email(user, otp):
    """
    Envoie un OTP à l'email de l'utilisateur.
    :param user: Instance `CustomUser`.
    :param otp: Code OTP à envoyer.
    """
    subject = "Votre Code OTP"
    message = f"Votre code OTP est : {otp}. Ce code est valide pour les 5 prochaines minutes."
    send_email(subject, message, [user.email])

def get_geolocation(ip_address):
    """
    Récupère la localisation géographique d'une adresse IP.
    :param ip_address: Adresse IP à localiser.
    :return: Tuple (ville, pays) ou (None, None) si échec.
    """
    if not getattr(settings, "IPSTACK_API_KEY", None):  # Vérifie si la clé API est définie
        return None, None

    try:
        response = requests.get(f"http://api.ipstack.com/{ip_address}?access_key={settings.IPSTACK_API_KEY}")
        if response.status_code == 200:
            data = response.json()
            return data.get("city"), data.get("country_name")
    except requests.RequestException:  # Gestion des erreurs de requête
        pass
    
    return None, None  # Retourne `None` si une erreur survient