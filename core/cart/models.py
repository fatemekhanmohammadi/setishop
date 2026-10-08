from django.db import models
from shop.models import Product
from django.contrib.auth import get_user_model
User = get_user_model()

# ===================================================================================================


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"سبد {self.user}"


# ==================================================================================================


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product}-{self.quantity}"


# ===================================================================================================

class Order(models.Model):
    class Statustype(models.TextChoices):
        PENDING = "PENDING", "pending"
        PAID = "PAID", "paid"
        SHIPPED = "SHIPPED", "shipped"
        CANCELLED = "CANCELLED", "cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=Statustype.choices, default=Statustype.PENDING)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.user}-{self.status}-{self.total_price}-{self.address}"


# ===================================================================================================


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order}-{self.product}-{self.quantity}"
