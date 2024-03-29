"""
Database Models

"""

import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

def recipe_image_file_path(instance,filename):
    "Geenrate filepath for new instance image"
    ext = os.path.splitext(filename)[1]
    filname = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads','recipe',filename)



class UserManager(BaseUserManager):
    """Manger for Users"""
    def create_user(self,email, password =None, **extra_fields):
        """create save return a user """
        if not email:
            raise ValueError("The user must have valid Email Address")
        user =self.model(email =self.normalize_email(email) , **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user 

    def create_superuser(self,email,password):
        """Create Super User"""
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
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


class Recipe(models.Model):
    """Recipe Objet"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length= 255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5,decimal_places=2)
    link = models.CharField(max_length=255,blank= True)
    tag=models.ManyToManyField('Tag')
    ingredients=models.ManyToManyField('Ingredient')
    image=models.ImageField(null=True,upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tags for filtering recipe"""
    name=models.CharField(max_length=255)
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipe"""
    name=models.CharField(max_length=255)
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name