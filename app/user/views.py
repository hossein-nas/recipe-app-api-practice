# Create your views here.
from rest_framework import generics

from user.serializers import UserSerializer


class UserAPIView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
