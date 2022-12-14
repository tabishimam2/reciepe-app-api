"""
Test for models

"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

class ModelTests(TestCase):
    """ Test models"""

    def test_create_user_with_email(self):
        """test creating user model with emial"""

        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password = password)

        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test to check the emails are normalized"""
        sample_emails = [
            ['test1@example.com','test1@example.com'],
            ['Test2@Example.com','Test2@example.com'],
            ['TEST3@EXAMPLE.COM','TEST3@example.com'],
            ['test4@example.COM','test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email,"sample123")
            self.assertEqual(user.email,expected)
    
    def test_new_user_without_email_raise_error(self):
        """Test to check the valid emails."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', "test123")

    def test_create_super_user(self):
        """Test to check SuperUser """
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test@123")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_reciepe(self):
        """Test create recipe is succesfull ."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title = 'Sample Recipe name',
            time_minutes= 5,
            price= Decimal('5.50'),
            description= 'Sample description of Recipe'
        )

        self.assertEqual(str(recipe), recipe.title)
