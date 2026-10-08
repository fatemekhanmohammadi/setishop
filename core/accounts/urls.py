from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

from . import views

urlpatterns = [
    path(
        "api/register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "api/profile/",
        views.ProfileUpdateView.as_view(),
        name="profile",
    ),
    path(
        "api/token/",
        views.CustomTokenObtainPairView.as_view(),
        name="token",
    ),
    path(
        "api/token/refresh/",
          TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/token/verify/",
        TokenVerifyView.as_view(),
        name="tokenverifyview",
    ),
    path(
        "api/password-reset/",
        views.PasswordResetRequestView.as_view(),
        name="password-reset",
    ),
    path(
        "api/password-reset/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
