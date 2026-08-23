from django.shortcuts import render
from .serializers import RegisterSerializer,ProfileSerializer
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model


User=get_user_model()
# Create your views here.


#================================================================================


class RegisterView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[permissions.AllowAny]


#=======================================================================================

class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset=User.objects.all()
    serializer_class=ProfileSerializer
    permission_classes=[permissions.IsAuthenticated]
    

    def get_object(self):
        return self.request.user

