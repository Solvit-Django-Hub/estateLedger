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
class UserManagementTests(APITestCase):

    def setUp(self):
        self.profile_url = reverse("profile")
        self.change_password_url = reverse("change-password")
        self.user_list_url = reverse("user-list")

        self.admin = User.objects.create_user(
            email="admin@example.com",
            phone_number="0788000001",
            role=User.Role.ADMIN,
            password="AdminPass123!",
            is_staff=True,
        )

        self.manager = User.objects.create_user(
            email="manager@example.com",
            phone_number="0788000002",
            role=User.Role.MANAGER,
            password="ManagerPass123!",
            is_staff=True,
        )

        self.owner = User.objects.create_user(
            email="owner@example.com",
            phone_number="0788000003",
            role=User.Role.OWNER,
            password="OwnerPass123!",
        )

        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            phone_number="0788000004",
            role=User.Role.TENANT,
            password="TenantPass123!",
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

    def test_authenticated_user_can_view_own_profile(self):
        self.authenticate(self.tenant)

        response = self.client.get(
            self.profile_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["email"],
            self.tenant.email
        )

        self.assertEqual(
            response.data["role"],
            User.Role.TENANT
        )

    def test_user_can_update_own_profile(self):
        self.authenticate(self.tenant)

        response = self.client.patch(
            self.profile_url,
            {
                "phone_number": "0788111111"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.tenant.refresh_from_db()

        self.assertEqual(
            self.tenant.phone_number,
            "0788111111"
        )

    def test_user_cannot_change_own_role(self):
        self.authenticate(self.tenant)

        response = self.client.patch(
            self.profile_url,
            {
                "role": User.Role.ADMIN
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.tenant.refresh_from_db()

        self.assertEqual(
            self.tenant.role,
            User.Role.TENANT
        )

    def test_wrong_old_password_is_rejected(self):
        self.authenticate(self.tenant)

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "WrongPassword123!",
                "new_password": "NewTenantPass123!",
                "new_password_confirmation": "NewTenantPass123!",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "old_password",
            response.data
        )

    def test_new_password_cannot_be_same_as_old_password(self):
        self.authenticate(self.tenant)

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "TenantPass123!",
                "new_password": "TenantPass123!",
                "new_password_confirmation": "TenantPass123!",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "new_password",
            response.data
        )

    def test_password_confirmation_must_match(self):
        self.authenticate(self.tenant)

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "TenantPass123!",
                "new_password": "NewTenantPass123!",
                "new_password_confirmation": "DifferentPass123!",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "new_password_confirmation",
            response.data
        )

    def test_user_can_change_password_successfully(self):
        self.authenticate(self.tenant)

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": "TenantPass123!",
                "new_password": "NewTenantPass123!",
                "new_password_confirmation": "NewTenantPass123!",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.tenant.refresh_from_db()

        self.assertTrue(
            self.tenant.check_password(
                "NewTenantPass123!"
            )
        )

        self.assertFalse(
            self.tenant.check_password(
                "TenantPass123!"
            )
        )

    def test_admin_can_view_all_users(self):
        self.authenticate(self.admin)

        response = self.client.get(
            self.user_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        results = response.data.get(
            "results",
            response.data
        )

        emails = [
            user["email"]
            for user in results
        ]

        self.assertIn(
            self.admin.email,
            emails
        )

        self.assertIn(
            self.manager.email,
            emails
        )

        self.assertIn(
            self.owner.email,
            emails
        )

        self.assertIn(
            self.tenant.email,
            emails
        )

    def test_manager_cannot_view_admin_users(self):
        self.authenticate(self.manager)

        response = self.client.get(
            self.user_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        results = response.data.get(
            "results",
            response.data
        )

        roles = [
            user["role"]
            for user in results
        ]

        self.assertNotIn(
            User.Role.ADMIN,
            roles
        )

    def test_owner_cannot_view_user_list(self):
        self.authenticate(self.owner)

        response = self.client.get(
            self.user_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_tenant_cannot_view_user_list(self):
        self.authenticate(self.tenant)

        response = self.client.get(
            self.user_list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )