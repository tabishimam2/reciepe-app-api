"""
URL mappings for the user API
"""

from venv import create
from django.urls import path
from user.views import views

app_name = 'user'

urlpatterns = [
    path('create/',views.CreateUserView.as_view(), name= 'create'),
]