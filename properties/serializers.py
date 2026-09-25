from rest_framework import serializers
from django.utils import timezone
from .models import Estate, Unit, UnitClaim, EstateMembership

class EstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = [
            'id',
            'name',
            'address',
            'description',
            'is_active',
            'created_at',

        ]
        read_only_fields= ['id', 'created_at']

    def validate_name(self, value):
        value = value.strip().upper()

        if len(value) < 3:
            raise serializers.ValidationError(
                "Estate name must be at least 3 characters."
            )
        return value

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = [
            'id',
            'estate',
            'unit_number',
            'unit_type',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_unit_number(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "Unit number cannot be empty."
            )

        return value

class UnitClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitClaim
        fields = [
            'id',
            'user',
            'unit',
            'role_at_unit',
            'status',
            'claimed_at',
            'confirmed_by',
            'confirmed_at',

        ]
        read_only_fields = ['claimed_at', 'confirmed_by', 'confirmed_at', 'status']

    def validate(self, data):

        user =data.get('user')
        unit = data.get('unit')
        role_at_unit =  data.get('role_at_unit')

        existing_claim= UnitClaim.objects.filter(
            user=user,
            unit=unit,
            role_at_unit =role_at_unit,
            status__in = [
                UnitClaim.Status.PENDING,
                UnitClaim.Status.CONFIRMED
            ],
        ).exists()

        if existing_claim:
            raise serializers.ValidationError(
                "User already has a pending claim for this unit and role"
            )
        return data

class EstateMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstateMembership
        fields = [
            'id',
            'user',
            'estate',
            'role',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    def validate(self, data):
        user = data.get("user")
        estate = data.get("estate")
        role = data.get("role")

        existing_membership = EstateMembership.objects.filter(
            user=user,
            estate=estate,
            role=role,
        ).exists()

        if existing_membership:
            raise serializers.ValidationError(
                "This user already has this role in this estate."
            )

        return data

class UnitClaimApprovalSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnitClaim
        fields = [
            "status",
        ]

    def validate_status(self, value):
        allowed_statuses = [
            UnitClaim.Status.CONFIRMED,
            UnitClaim.Status.REJECTED,
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Status must be either confirmed or rejected."
            )

        return value

    def update(self, instance, validated_data):
        status = validated_data.get("status")

        instance.status = status

        if status == UnitClaim.Status.CONFIRMED:
            instance.confirmed_by = self.context["request"].user
            instance.confirmed_at = timezone.now()

        elif status == UnitClaim.Status.REJECTED:
            instance.confirmed_by = self.context["request"].user
            instance.confirmed_at = timezone.now()

        instance.save()

        return instance