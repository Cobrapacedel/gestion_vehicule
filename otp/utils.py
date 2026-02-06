import secrets
import phonenumbers
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP
import requests
from twilio.rest import Client


# --- Génération OTP ---
def generate_otp(length=6):
    """
    Génère un OTP numérique aléatoire sécurisé.
    """
    return str(secrets.randbelow(10**length)).zfill(length)


# --- Validation numéro ---
def validate_phone(phone):
    """
    Valide un numéro de téléphone international.
    """
    try:
        parsed = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError("Numéro de téléphone invalide.")
    except phonenumbers.NumberParseException:
        raise ValidationError("Format de numéro de téléphone incorrect.")


# --- Envoi Email ---
def send_email(subject, message, recipient_list):
    """
    Envoie un email avec Django.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


def send_otp_via_email(user_email, otp_code):
    """
    Envoie l’OTP par email.
    """
    subject = "Votre code OTP"
    message = f"Voici votre code OTP : {otp_code}. Il expire dans 5 minutes."
    send_email(subject, message, [user_email])


# --- Envoi SMS ---
def send_sms(to_number, message):
    """
    Envoie un SMS via Twilio, ou affiche un message en mode dev.
    """
    if not getattr(settings, "TWILIO_ACCOUNT_SID", None) or not getattr(settings, "TWILIO_AUTH_TOKEN", None):
        print(f"[DEBUG - SMS non envoyé] À: {to_number} | Message: {message}")
        return

    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_PHONE_NUMBER

    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_=from_number,
        to=to_number
    )


def send_otp_via_sms(user_phone, otp_code):
    """
    Envoie l’OTP par SMS.
    """
    message = f"Votre code OTP est : {otp_code}. Valable 5 minutes."
    send_sms(user_phone, message)


# --- Envoi principal selon la méthode ---
def send_otp(user, otp):
    """
    Envoie l’OTP par email ou SMS selon les préférences de l’utilisateur.
    :param user: instance de CustomUser
    :param otp: instance du modèle OTP
    """
    if otp.delivery_method == 'email':
        send_otp_via_email(user.email, otp.code)
    elif otp.delivery_method == 'sms':
        if user.phone:
            send_otp_via_sms(user.phone, otp.code)
        else:
            raise ValueError("Numéro de téléphone non défini pour cet utilisateur.")
    else:
        raise ValueError("Méthode de livraison invalide.")


# --- Géolocalisation par IP ---
def get_geolocation(ip_address):
    """
    Récupère la ville et le pays à partir d'une IP via IPStack.
    """
    if not getattr(settings, "IPSTACK_API_KEY", None):
        return None, None

    try:
        response = requests.get(
            f"http://api.ipstack.com/{ip_address}?access_key={settings.IPSTACK_API_KEY}"
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("city"), data.get("country_name")
    except requests.RequestException:
        pass

    return None, None


# --- Génération et envoi ---
def generate_and_send_otp(user, method='email'):
    """
    Génère un OTP pour l'utilisateur, le sauvegarde et l'envoie.
    """
    if method not in ['email', 'sms']:
        raise ValueError('Metòd livrezon an pa bon')
    code = generate_otp()
    otp = OTP.objects.create(user=user, code=code, delivery_method=method)
    send_otp(user, otp)