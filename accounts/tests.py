from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")
        self.logout_url = reverse("logout")

        self.user_data = {
            "email": "tenant1@example.com",
            "phone_number": "0788000001",
            "role": "tenant",
            "password": "StrongPass123!",
            "password_confirmation": "StrongPass123!",
        }

    def test_user_can_register(self):
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            User.objects.filter(
                email="tenant1@example.com"
            ).exists()
        )

    def test_duplicate_email_is_rejected(self):
        self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )

        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_password_confirmation_must_match(self):
        data = self.user_data.copy()

        data["password_confirmation"] = "WrongPassword123!"

        response = self.client.post(
            self.register_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "password_confirmation",
            response.data
        )

    def test_user_can_login_and_receive_tokens(self):
        User.objects.create_user(
            email="tenant1@example.com",
            phone_number="0788000001",
            role="tenant",
            password="StrongPass123!"
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "tenant1@example.com",
                "password": "StrongPass123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_invalid_login_is_rejected(self):
        User.objects.create_user(
            email="tenant1@example.com",
            phone_number="0788000001",
            role="tenant",
            password="StrongPass123!"
        )

        response = self.client.post(
            self.login_url,
            {
                "email": "tenant1@example.com",
                "password": "WrongPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_refresh_token_returns_new_access_token(self):
        user = User.objects.create_user(
            email="tenant1@example.com",
            phone_number="0788000001",
            role="tenant",
            password="StrongPass123!"
        )

        refresh = RefreshToken.for_user(user)

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "access",
            response.data
        )

    def test_authenticated_user_can_logout(self):
        user = User.objects.create_user(
            email="tenant1@example.com",
            phone_number="0788000001",
            role="tenant",
            password="StrongPass123!"
        )

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        response = self.client.post(
            self.logout_url,
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_blacklisted_refresh_token_cannot_be_used(self):
        user = User.objects.create_user(
            email="tenant1@example.com",
            phone_number="0788000001",
            role="tenant",
            password="StrongPass123!"
        )

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        logout_response = self.client.post(
            self.logout_url,
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(
            logout_response.status_code,
            status.HTTP_200_OK
        )

        self.client.credentials()

        refresh_response = self.client.post(
            self.refresh_url,
            {
                "refresh": str(refresh)
            },
            format="json"
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )