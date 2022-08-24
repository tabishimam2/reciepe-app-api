"""
Serializers for api view
"""

from dataclasses import field
from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializers for the users"""

    class Meta:
        model = get_user_model()
        fields = ['email','password','name']
        extra_kwargs = {'password':{'write_only':True, 'min_lenght': 5}}

    def create(self,validate_data):
        """Create and return an user with encrypted password"""
        return get_user_model().objects.create_user(**validate_data)

    