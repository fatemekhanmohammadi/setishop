from django.db import transaction
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from shop.models import Product

from .models import Order, OrderItem
from .serializers import OrderSerializer
from .tasks import send_order_confirmation_email

# ===============================================================================================================


@extend_schema(
    tags=["Cart"],
    examples=[
        OpenApiExample(
            "نمونه درخواست",
            value={"address": "تهران، خیابان آزادی"},
            request_only=True,
        ),
        OpenApiExample(
            "نمونه پاسخ موفق",
            value={
                "message": "سفارش با موفقیت ثبت شد",
                "order_id": 12,
                "total_price": 1550000,
            },
            response_only=True,
        ),
    ],
)
class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.cartitem_set.exists():
            return Response(
                {"error": "سبد خرید شما خالی است"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        address = request.data.get("address", "")
        shipping_cost = 50000

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    shipping_cost=shipping_cost,
                    total_price=0,
                )

                total = 0

                for item in cart.cartitem_set.select_related("product").all():
                    product = Product.objects.select_for_update().get(
                        id=item.product.id
                    )

                    if product.stock < item.quantity:
                        raise Exception(f"موجودی کافی برای {product.title} نیست")

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price_at_purchase=product.price,
                    )

                    product.stock -= item.quantity
                    product.save()

                    total += product.price * item.quantity

                order.total_price = total + shipping_cost
                order.save()

                cart.cartitem_set.all().delete()

                try:
                    send_order_confirmation_email.delay(order.id)
                except Exception:
                    pass

            return Response(
                {
                    "message": "سفارش با موفقیت ثبت شد",
                    "order_id": order.id,
                    "total_price": order.total_price,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


# =============================================================================================================


@extend_schema(tags=["Cart"])
class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


# =============================================================================================================


@extend_schema(tags=["Cart"])
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
