from .models import Order, OrderItem
from rest_framework import serializers


# ================================================================================================================

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_purchase']

# ================================================================================================================


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price',
                  'shipping_cost', 'address', 'items', 'created_at']

# ================================================================================================================
