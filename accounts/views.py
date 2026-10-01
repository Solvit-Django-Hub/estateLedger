from rest_framework import (status, serializers)
from .utils import send_activation_email
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    ListAPIView,
)
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
    LogoutSerializer,
    StaffCreateSerializer,
    StaffStatusSerializer,
    ProfileSerializer,
    ChangePasswordSerializer,
)
User = get_user_model()
class CustomTokenRefreshView(TokenRefreshView):

    @extend_schema(
        tags=["Authentication"],
        summary="Refresh access token",
        description="Generates a new access token using a valid refresh token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegistrationSerializer,
        responses={201: UserSerializer},
        tags=["Authentication"],
        summary="Register a new user",
    )
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        send_activation_email(user, request)
        return Response(
            {
                "message": (
                    "User registered successfully."
                    "Please check your email to activate your account."
                ),
                
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )

class ActivateAccountAPIView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        summary="Activate user account",
        description="Activates a user account using the UID and token sent by email.",
        responses={
            200: inline_serializer(
                name="AccountActivationSuccessResponse",
                fields={
                    "message": serializers.CharField(),
                },
            ),
            400: inline_serializer(
                name="AccountActivationErrorResponse",
                fields={
                    "error": serializers.CharField(),
                },
            ),
        },
        tags=["Authentication"],
    )
    def get(self, request, uidb64, token):
        try:
            user_id = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = User.objects.get(pk=user_id)

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {
                    "error": "Invalid activation link."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {
                    "error": "Invalid or expired activation token."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {
                "message": "Account activated successfully."
            },
            status=status.HTTP_200_OK,
        )

class StaffCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=StaffCreateSerializer,
        responses={201: UserSerializer},
        tags=["Staff Management"],
        summary="Create a new staff user",
    )
    def post(self, request):

        if request.user.role != User.Role.ADMIN:
            return Response(
                {
                    "error":
                    "Only administrators can create staff users."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = StaffCreateSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        activation_url = send_activation_email(
            user,
            request
        )

        return Response(
            {
                "message":
                "Staff user created successfully. "
                "Activation email has been sent.",
                "activation_url": activation_url,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )
        
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserSerializer},
        tags=["Authentication"],
        summary="Login user"
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={200: dict},
        tags=["Authentication"],
        summary="Logout user",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "message": "Logout successful."
                },
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {
                    "error": "Invalid or expired refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class StaffStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=StaffStatusSerializer,
        responses={200: UserSerializer},
        tags=["Staff Management"],
        summary="Promote or demote a user",
        description=(
            "Promotes an activated normal user to staff, "
            "or demotes a staff member back to a normal user."
        ),
    )
    def patch(self, request, user_id):

        if request.user.role != User.Role.ADMIN:
            return Response(
                {
                    "error":
                    "Only administrators can promote or demote staff."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(pk=user_id)

        except User.DoesNotExist:
            return Response(
                {
                    "error": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StaffStatusSerializer(
            user,
            data=request.data,
            context={
                "request": request
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        action = serializer.validated_data["action"]

        if action == "promote":
            message = (
                "User promoted to staff successfully."
            )
        else:
            message = (
                "Staff user demoted successfully."
            )

        return Response(
            {
                "message": message,
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @extend_schema(
        tags=["User Management"],
        summary="View or update profile",
        description=(
            "Allows the authenticated user to view "
            "or update their own profile."
        ),
    )
    def get(self, request, *args, **kwargs):
        return super().get(
            request,
            *args,
            **kwargs
        )

    @extend_schema(
        tags=["User Management"],
        summary="Update profile",
        description=(
            "Allows the authenticated user to update "
            "their email or phone number."
        ),
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(
            request,
            *args,
            **kwargs
        )

    @extend_schema(
        tags=["User Management"],
        summary="Replace profile information",
    )
    def put(self, request, *args, **kwargs):
        return super().put(
            request,
            *args,
            **kwargs
        )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: dict},
        tags=["User Management"],
        summary="Change password",
        description=(
            "Allows an authenticated user to change "
            "their password after confirming the old password."
        ),
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={
                "request": request
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = request.user

        user.set_password(
            serializer.validated_data[
                "new_password"
            ]
        )

        user.save()

        return Response(
            {
                "message":
                "Password changed successfully."
            },
            status=status.HTTP_200_OK,
        )

class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.Role.ADMIN:
            return User.objects.all().order_by("id")

        if user.role == User.Role.MANAGER:
            return User.objects.exclude(
                role=User.Role.ADMIN
            ).order_by("id")

        return User.objects.none()

    def list(self, request, *args, **kwargs):

        if request.user.role not in [
            User.Role.ADMIN,
            User.Role.MANAGER,
        ]:
            return Response(
                {
                    "error":
                    "You do not have permission "
                    "to view the user list."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().list(
            request,
            *args,
            **kwargs
        )
