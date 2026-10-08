import requests
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Order

from .models import Payment

MERCHANT_ID = "1952217b-a176-4c48-9012-8e3a5d7c6097"  # تو .env بذار بعداً
ZARINPAL_REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_VERIFY_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
ZARINPAL_STARTPAY_URL = "https://sandbox.zarinpal.com/pg/StartPay/"

# =======================================================================================================================


@extend_schema(tags=["Pyments"])
class PaymentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response(
                {"error": "سفارش یافت نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        payment, created = Payment.objects.get_or_create(
            order=order, defaults={"amount": order.total_price}
        )

        data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(order.total_price),
            "callback_url": "http://127.0.0.1:8000/payments/api/payments/verify/",
            "description": f"پرداخت سفارش {order.id}",
        }

        response = requests.post(ZARINPAL_REQUEST_URL, json=data, timeout=10)

        print("ZARINPAL STATUS:", response.status_code)
        print("ZARINPAL RESPONSE:", response.text)

        result = response.json()

        if result.get("data") and result["data"].get("code") == 100:
            authority = result["data"]["authority"]
            payment.authority = authority
            payment.save()
            return Response({"payment_url": ZARINPAL_STARTPAY_URL + authority})

        return Response(
            {"error": "خطا در اتصال به درگاه پرداخت"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# =========================================================================================================================


@extend_schema(tags=["Pyments"])
class PaymentVerifyView(APIView):
    def get(self, request):
        authority = request.GET.get("Authority")
        payment = Payment.objects.filter(authority=authority).first()

        if not payment:
            return Response(
                {"error": "تراکنش یافت نشد"}, status=status.HTTP_404_NOT_FOUND
            )

        # idempotent: اگه قبلاً پردازش شده، دوباره پردازش نکن
        if payment.status == Payment.StatusType.PAID:
            return Response({"message": "این تراکنش قبلاً تایید شده است"})

        data = {
            "merchant_id": MERCHANT_ID,
            "amount": int(payment.amount),
            "authority": authority,
        }
        response = requests.post(ZARINPAL_VERIFY_URL, json=data, timeout=10)
        result = response.json()

        if result.get("data") and result["data"].get("code") == 100:
            payment.status = Payment.StatusType.PAID
            payment.ref_id = result["data"]["ref_id"]
            payment.save()

            payment.order.status = "PAID"
            payment.order.save()

            return Response(
                {"message": "پرداخت با موفقیت انجام شد", "ref_id": payment.ref_id}
            )

        payment.status = Payment.StatusType.FAILED
        payment.save()
        return Response(
            {"error": "پرداخت ناموفق بود"}, status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================================================================================
