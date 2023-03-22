# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, \
    AuthTokenSerializer, UserListSerializer

User = get_user_model()


class UserAPIView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.all()


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
