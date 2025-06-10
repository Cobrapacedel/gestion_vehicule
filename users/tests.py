from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Profile, OTP, LoginAttempt, LoginHistory
from .forms import CustomUserCreationForm, CustomAuthenticationForm, OTPVerificationForm
from .utils import generate_otp, validate_phone_number, send_email, get_geolocation
from .signals import create_user_profile
from unittest.mock import patch

# Get the CustomUser model
CustomUser = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            phone_number="+1234567890"
        )

    def test_create_user(self):
        """Test creating a new user."""
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertFalse(self.user.is_verified)
        self.assertTrue(self.user.is_active)

    def test_unique_email(self):
        """Test that email must be unique."""
        with self.assertRaises(ValidationError):
            CustomUser.objects.create_user(email="test@example.com", password="password123")

    def test_phone_number_validation(self):
        """Test phone number validation."""
        invalid_phone = "+123invalid"
        with self.assertRaises(ValidationError):
            validate_phone_number(invalid_phone)

    def test_profile_creation_signal(self):
        """Test that a profile is created automatically when a user is created."""
        profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, self.user)


class OTPModelTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = CustomUser.objects.create_user(
            email="otpuser@example.com",
            password="password123"
        )
        self.otp = OTP.objects.create(user=self.user, code=generate_otp())

    def test_otp_validity(self):
        """Test OTP validity."""
        self.assertTrue(self.otp.is_valid())
        # Expire the OTP
        self.otp.expires_at = timezone.now() - timedelta(minutes=1)
        self.otp.save()
        self.assertFalse(self.otp.is_valid())


class ViewTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email="viewuser@example.com",
            password="password123"
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_user_registration_view(self):
        """Test user registration view."""
        response = self.client.post(reverse("register"), {
            "email": "newuser@example.com",
            "phone_number": "+1987654321",
            "first_name": "New",
            "last_name": "User",
            "password1": "password123",
            "password2": "password123",
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(CustomUser.objects.filter(email="newuser@example.com").exists())

    def test_user_login_view(self):
        """Test user login view."""
        response = self.client.post(reverse("login"), {
            "username": "viewuser@example.com",
            "password": "password123",
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_otp_verification_view(self):
        """Test OTP verification view."""
        otp = OTP.objects.create(user=self.user, code=generate_otp())
        response = self.client.post(reverse("otp-verification"), {"code": otp.code})
        self.assertEqual(response.status_code, 302)  # Redirect after successful OTP verification
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)


class FormTests(TestCase):
    def test_custom_user_creation_form(self):
        """Test CustomUserCreationForm."""
        form_data = {
            "email": "formuser@example.com",
            "phone_number": "+1123456789",
            "first_name": "Form",
            "last_name": "User",
            "password1": "password123",
            "password2": "password123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_otp_verification_form(self):
        """Test OTPVerificationForm with invalid OTP."""
        form_data = {"code": "123456"}
        form = OTPVerificationForm(data=form_data)
        self.assertFalse(form.is_valid())


class UtilsTests(TestCase):
    @patch("requests.get")
    def test_get_geolocation(self, mock_get):
        """Test geolocation utility function."""
        mock_response = mock_get.return_value
        mock_response.json.return_value = {"city": "Paris", "country_name": "France"}
        city, country = get_geolocation("127.0.0.1")
        self.assertEqual(city, "Paris")
        self.assertEqual(country, "France")


class SignalTests(TestCase):
    def test_profile_signal(self):
        """Test profile creation signal."""
        user = CustomUser.objects.create_user(email="signaluser@example.com", password="password123")
        self.assertTrue(Profile.objects.filter(user=user).exists())


class MiddlewareTests(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email="middlewareuser@example.com",
            password="password123"
        )

    def test_account_lock_middleware(self):
        """Test account locking middleware."""
        login_attempt = LoginAttempt.objects.create(user=self.user, failed_attempts=3)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)  # Redirect to login page if account is locked