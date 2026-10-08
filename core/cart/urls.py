from django.urls import path
from . import views

urlpatterns = [
    path('api/orders/checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('api/orders/', views.OrderListView.as_view(), name='order-list'),
    path('api/orders/<int:pk>/',
         views.OrderDetailView.as_view(), name='order-detail'),
]
