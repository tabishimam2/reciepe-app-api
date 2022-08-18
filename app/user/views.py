""""
Views for user API
"""

from django.shortcuts import render
from rest_framework import generics
from user.serializers import UserSerializer
# Create your views here.


class CreateUserView(generics.CreateAPIView):
    """Create a new system in the system """
    serializer_class = UserSerializer
