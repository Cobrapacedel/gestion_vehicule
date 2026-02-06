# fines/utils.py
from django.core.mail import send_mail

def send_payment_notification(user, message):
    if user.email:
        send_mail(
            subject="Notification de paiement",
            message=message,
            from_email="no-reply@tonsite.com",
            recipient_list=[user.email],
            fail_silently=True,
        )