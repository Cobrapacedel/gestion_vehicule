from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from .models import LoginAttempt
from otp.models import OTP

# Get the CustomUser model
CustomUser = get_user_model()

class EmailAuthBackend(BaseBackend):
    """
    Custom authentication backend for authenticating users using their email and password.
    Also handles account locking based on failed login attempts.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate a user based on their email and password.
        :param request: The HTTP request object.
        :param email: The email provided by the user.
        :param password: The password provided by the user.
        :return: The authenticated user or None if authentication fails.
        """
        try:
            # Fetch the user by email
            user = CustomUser.objects.get(email=email)

            # Check if the account is locked
            login_attempt, created = LoginAttempt.objects.get_or_create(user=user)
            if login_attempt.is_locked():
                return None  # Account is locked, deny access

            # Verify the password
            if user.check_password(password) and self.user_can_authenticate(user):
                # Reset failed attempts on successful login
                login_attempt.reset_attempts()
                return user
            else:
                # Increment failed attempts
                login_attempt.register_failed_attempt()
        except CustomUser.DoesNotExist:
            # User with the given email does not exist
            return None

    def get_user(self, user_id):
        """
        Retrieve a user by their ID.
        :param user_id: The ID of the user.
        :return: The user instance or None if the user does not exist.
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """
        Check if the user is allowed to authenticate.
        :param user: The user instance.
        :return: True if the user is active, False otherwise.
        """
        return user.is_active


class OTPAuthBackend(BaseBackend):
    """
    Custom authentication backend for verifying OTPs during two-factor authentication (2FA).
    """

    def authenticate(self, request, email=None, otp=None, **kwargs):
        """
        Authenticate a user based on their email and OTP.
        :param request: The HTTP request object.
        :param email: The email provided by the user.
        :param otp: The OTP provided by the user.
        :return: The authenticated user or None if authentication fails.
        """
        try:
            # Fetch the user by email
            user = CustomUser.objects.get(email=email)

            # Check if the OTP is valid
            otp_record = user.otps.filter(code=otp).first()
            if otp_record and otp_record.is_valid():
                # Mark the user as verified
                user.is_verified = True
                user.save()
                return user
        except CustomUser.DoesNotExist:
            # User with the given email does not exist
            return None

    def get_user(self, user_id):
        """
        Retrieve a user by their ID.
        :param user_id: The ID of the user.
        :return: The user instance or None if the user does not exist.
        """
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None