from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from .models import Cart

# ==========================================================================================================================


@shared_task
def send_order_confirmation_email(order_id):
    from .models import Order

    order = Order.objects.filter(id=order_id).first()
    if order:
        send_mail(
            subject=f"تایید سفارش #{order.id}",
            message=f"سفارش شما با مبلغ {order.total_price} ثبت شد.",
            from_email="noreply@setishop.com",
            recipient_list=[order.user.email],
            fail_silently=False,
        )


# ==========================================================================================================================


@shared_task
def send_abandoned_cart_emails():
    threshold = timezone.now() - timedelta(hours=24)
    abandoned_carts = Cart.objects.filter(
        created_atlt=threshold, cartitemisnull=False
    ).distinct()

    for cart in abandoned_carts:
        send_mail(
            subject="سبد خرید شما منتظر شماست!",
            message="محصولاتی در سبد خرید شما باقی مانده. برای تکمیل خرید کلیک کنید.",
            from_email="noreply@setishop.com",
            recipient_list=[cart.user.email],
        )
