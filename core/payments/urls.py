from django.urls import path
from . import views

urlpatterns = [
    path('api/payments/request/<int:order_id>/', views.PaymentRequestView.as_view(), name='payment-request'),
    path('api/payments/verify/', views.PaymentVerifyView.as_view(), name='payment-verify'),
]