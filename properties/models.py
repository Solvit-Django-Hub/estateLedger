from django.db import models

# Create your models here.
from django.conf import settings



class Estate(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.PROTECT, related_name="units")
    unit_number = models.CharField(max_length=50)
    unit_type = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["estate", "unit_number"], name="unique_unit_number_per_estate"
            )
        ]

    def __str__(self):
        return f"{self.estate.name} - {self.unit_number}"


class UnitClaim(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        TENANT = "tenant", "Tenant"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"
        INACTIVE = "inactive", "Inactive"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="unit_claims"
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="claims")
    role_at_unit = models.CharField(max_length=10, choices=Role.choices)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    claimed_at = models.DateTimeField(auto_now_add=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claims_confirmed",
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            # Prevents the same person from double-claiming the same unit
            # with a live (pending/confirmed) claim in the same role.
            models.UniqueConstraint(
                fields=["user", "unit", "role_at_unit"],
                condition=models.Q(status__in=["pending", "confirmed"]),
                name="unique_live_claim_per_user_unit_role",
            )
        ]

    def __str__(self):
        return f"{self.user} -> {self.unit} ({self.role_at_unit}, {self.status})"


class EstateMembership(models.Model):
    

    class EstateRole(models.TextChoices):
        MANAGER = "manager", "Manager"
        ADMIN = "admin", "Administrator"
        BOARD = "board", "Board / Association Member"
        ACCOUNTANT = "accountant", "Accountant"
        AUDITOR = "auditor", "Auditor"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="estate_memberships"
    )
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=EstateRole.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "estate", "role"], name="unique_membership_role"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.estate} ({self.role})"