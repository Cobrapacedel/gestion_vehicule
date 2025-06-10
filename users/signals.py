from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile, OTP
from .utils import generate_otp

# Get the CustomUser model
CustomUser = get_user_model()

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a profile when a new user is created.
    :param sender: The model class sending the signal (CustomUser).
    :param instance: The instance of the model being saved.
    :param created: A boolean indicating if the instance was just created.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the user's profile whenever the user is saved.
    :param sender: The model class sending the signal (CustomUser).
    :param instance: The instance of the model being saved.
    """
    instance.profile.save()

@receiver(pre_save, sender=CustomUser)
def set_default_values(sender, instance, **kwargs):
    """
    Set default values for fields like `is_verified` before saving the user.
    :param sender: The model class sending the signal (CustomUser).
    :param instance: The instance of the model being saved.
    """
    if not hasattr(instance, "is_verified"):
        instance.is_verified = False  # Ensure `is_verified` defaults to False

@receiver(post_save, sender=CustomUser)
def generate_initial_otp(sender, instance, created, **kwargs):
    """
    Generate an initial OTP for the user after registration.
    :param sender: The model class sending the signal (CustomUser).
    :param instance: The instance of the model being saved.
    :param created: A boolean indicating if the instance was just created.
    """
    if created:
        otp_code = generate_otp()
        OTP.objects.create(user=instance, code=otp_code)
        # TODO: Send the OTP to the user via email or SMS using `send_otp_via_email` or similar utility.