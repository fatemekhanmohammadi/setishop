from django.contrib import admin

# Register your models here.
from .models import Cart, Order, OrderItem, CartItem


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
