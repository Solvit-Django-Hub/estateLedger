from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "role",
            "last_login",
        )
        read_only_fields = ("id", "last_login")


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    password_confirmation = serializers.CharField(
        write_only=True
    )
    role = serializers.ChoiceField(
        choices = [
            (User.Role.OWNER, User.Role.OWNER.label),
            (User.Role.TENANT, User.Role.TENANT.label),
        ]
    )

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "role",
            "password",
            "password_confirmation",
        )

        read_only_fields = ("id",)

    def validate_phone_number(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain digits only."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        if not value.startswith("07"):
            raise serializers.ValidationError(
                "Phone number must start with 07"
            )

        return value

    def to_internal_value(self, data):
        data = data.copy()

        if "role" in data and isinstance(data["role"], str):
            data["role"] = data["role"].strip().lower()

        return super().to_internal_value(data)

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirmation"):
            raise serializers.ValidationError(
                {
                    "password_confirmation":
                    "Passwords do not match."
                }
            )

        attrs.pop("password_confirmation")

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            is_active=False,
            **validated_data
        )

        return user


class StaffCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    role = serializers.ChoiceField(
        choices=[
            (User.Role.ADMIN, User.Role.ADMIN.label),
            (User.Role.MANAGER, User.Role.MANAGER.label),
        ]
    )

    class Meta:
        model = User
        fields = ("id", "email","phone_number","role","password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            is_staff=True,
            is_active=False,
            **validated_data
        )

        return user

class StaffStatusSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=[
            ("promote", "Promote"),
            ("demote", "Demote"),
        ]
    )

    role = serializers.ChoiceField(
        choices=User.Role.choices
    )

    def validate(self, attrs):
        action = attrs.get("action")
        role = attrs.get("role")

        if action == "promote":
            if role not in [
                User.Role.ADMIN,
                User.Role.MANAGER,
            ]:
                raise serializers.ValidationError({
                    "role":
                    "A promoted staff user must be admin or manager."
                })

            if self.instance and not self.instance.is_active:
                raise serializers.ValidationError({
                    "user":
                    "Only activated users can be promoted to staff."
                })

        if action == "demote":
            if role not in [
                User.Role.OWNER,
                User.Role.TENANT,
            ]:
                raise serializers.ValidationError({
                    "role":
                    "A demoted staff user must become owner or tenant."
                })

            if self.instance and not self.instance.is_staff:
                raise serializers.ValidationError({
                    "user":
                    "This user is not currently a staff member."
                })

        request = self.context.get("request")

        if (
            self.instance
            and request
            and self.instance == request.user
            and action == "demote"
        ):
            raise serializers.ValidationError({
                "user":
                "You cannot demote your own staff account."
            })

        return attrs

    def update(self, instance, validated_data):
        action = validated_data["action"]
        role = validated_data["role"]

        if action == "promote":
            instance.role = role
            instance.is_staff = True

        elif action == "demote":
            instance.role = role
            instance.is_staff = False

        instance.save(
            update_fields=[
                "role",
                "is_staff",
            ]
        )

        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        user = User.objects.filter(email__iexact=email).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError(
                "Account is not activated. Please check your email."
            )
        attrs["user"] = user
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "role",
            "last_login",
        )

        read_only_fields = (
            "id",
            "role",
            "last_login",
        )

    def validate_phone_number(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone number must contain digits only."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        if not value.startswith("07"):
            raise serializers.ValidationError(
                "Phone number must start with 07."
            )

        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    new_password_confirmation = serializers.CharField(
        write_only=True
    )

    def validate_old_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Old password is incorrect."
            )

        return value

    def validate(self, attrs):
        user = self.context["request"].user

        old_password = attrs["old_password"]
        new_password = attrs["new_password"]
        confirmation = attrs["new_password_confirmation"]

        # Check confirmation
        if new_password != confirmation:
            raise serializers.ValidationError(
                {
                    "new_password_confirmation":
                    "New passwords do not match."
                }
            )

        # New password must be different
        if user.check_password(new_password):
            raise serializers.ValidationError(
                {
                    "new_password":
                    "New password cannot be the same as the old password."
                }
            )

        return attrs
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

