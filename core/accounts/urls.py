from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView,TokenVerifyView



urlpatterns = [

    path('api/register/',views.RegisterView.as_view(), name='register'),
    path('api/profile/',views.ProfileUpdateView.as_view(), name='profile'),

    path('api/token/', TokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='tokenverifyview'),

]