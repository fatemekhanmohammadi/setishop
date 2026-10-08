from django.db import models

from cart.models import Order


class Payment(models.Model):
    class StatusType(models.TextChoices):
        PENDING = "PENDING", "pending"
        PAID = "PAID", "paid"
        FAILED = "FAILED", "failed"

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    authority = models.CharField(max_length=100, blank=True)
    ref_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=StatusType.choices, default=StatusType.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.status}"
