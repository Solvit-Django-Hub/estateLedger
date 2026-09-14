from django.db import models

# Create your models here.

from properties.models import Estate, Unit


class ChargeType(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name="charge_types")
    # Supports "per unit or unit type" (spec 2.3). Null/blank = applies estate-wide.
    unit_type = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=100)
    default_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_recurring = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.estate.name} - {self.name}"


class Charge(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="charges")
    charge_type = models.ForeignKey(ChargeType, on_delete=models.PROTECT, related_name="charges")
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    # Tracks late-payment escalation (spec 2.3) without mutating amount_due,
    # so the original billed amount stays auditable.
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    penalty_applied_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_due(self):
        return self.amount_due + self.penalty_amount

    def __str__(self):
        return f"{self.unit} - {self.charge_type.name} due {self.due_date}"


class Invoice(models.Model):
    class Status(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    charge = models.OneToOneField(Charge, on_delete=models.PROTECT, related_name="invoice")
    invoice_number = models.CharField(max_length=30, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.invoice_number