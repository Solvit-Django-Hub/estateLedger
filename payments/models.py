from django.db import models

# Create your models here.
from django.conf import settings

from billing.models import Invoice


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        MTN = "mtn", "MTN Mobile Money"
        AIRTEL = "airtel", "Airtel Money"
        CARD = "card", "Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"

    class Status(models.TextChoices):
        # Required because MTN/Airtel confirmation is async (spec 2.4, 2.5):
        # a payment is initiated, then confirmed or failed by a webhook,
        # not by the request/response cycle that created it.
        PENDING = "pending", "Pending"
        SUCCESSFUL = "successful", "Successful"
        FAILED = "failed", "Failed"
        REVERSED = "reversed", "Reversed"

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments_made",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    payer_name = models.CharField(max_length=100, blank=True, null=True)
    # Gateway/bank reference used to match async webhook confirmations
    # back to this payment. Referenced in the original design's constraints
    # section but never actually defined there — added here.
    transaction_reference = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    initiated_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["transaction_reference"]),
            models.Index(fields=["status"]),
            models.Index(fields=["initiated_at"]),
        ]

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.amount} ({self.status})"


class Receipt(models.Model):
    # Only issued once a Payment.status == successful — enforce this in the
    # service layer that creates receipts, not here.
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, related_name="receipt")
    receipt_number = models.CharField(max_length=30, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="receipts/", null=True, blank=True)

    def __str__(self):
        return self.receipt_number