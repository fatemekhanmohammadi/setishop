from django.shortcuts import render
from .serializers import RegisterSerializer,ProfileSerializer
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
User=get_user_model()
from rest_framework_simplejwt.views import TokenObtainPairView
from cart.utils import merge_session_cart_to_db
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tasks import send_password_reset_email
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework.response import Response
from rest_framework import status

token_generator = PasswordResetTokenGenerator()
from rest_framework_simplejwt.views import TokenRefreshView,TokenVerifyView


#================================================================================

@extend_schema(tags=['accounts'])

class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]


#=======================================================================================
@extend_schema(tags=['accounts'])

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset=User.objects.all()
    serializer_class=ProfileSerializer
    permission_classes=[permissions.IsAuthenticated]
    

    def get_object(self):
        return self.request.user

#=======================================================================================
@extend_schema(tags=['accounts'])

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response= super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username')
            user = User.objects.filter(username=username).first()
            if user:
              merge_session_cart_to_db(request, user)
        return response

#=============================================================================

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            reset_link = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"
            send_password_reset_email.delay(user.email, reset_link)

        # همیشه پیام یکسان برمی‌گردونیم، حتی اگه ایمیل نباشه (برای امنیت، تا کسی نفهمه چه ایمیلی تو سیستم هست)
        return Response({'message': 'اگر این ایمیل در سیستم ثبت شده باشد، لینک بازیابی ارسال شد'})

#=============================================================================

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'لینک نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({'error': 'لینک منقضی شده یا نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'رمز عبور با موفقیت تغییر یافت'})


#=============================================================================
