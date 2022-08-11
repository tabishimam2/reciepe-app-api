"""
Database Models

"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

# Create your models here.

class UserManager(BaseUserManager):
    """Manger for Users"""
    def create_user(self,email, password =None, **extra_fields):
        """create save return a user """
        user =self.model(email = email , **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user 

class User(AbstractBaseUser,PermissionsMixin):
    """ User Model"""
    email = models.EmailField(max_length=255, unique= True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default= True)
    is_staff = models.BooleanField(default = False)

    objects= UserManager()
    USERNAME_FIELD = 'email'
