"""
Test for creating Ingredients
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENR_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    """Create and return an ingredient detail url"""
    return reverse('recipe:ingredient-detail',args=[ingredient_id])

def create_user(email='user@example.com', password='pass123'):
    return get_user_model().objects.create_user(email=email,password=password)

class PublicIngredientApiTests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required for retrieving ingredient"""
        res= self.client.get(INGREDIENR_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)



class PrivateIngredientApiTest(TestCase):
    """Test authenticated API request"""

    def setUp(self) -> None:
        self.user=create_user()
        self.client=APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_ingredients(self):
        """Test reteriving a list of ingredients"""
        Ingredient.objects.create(user=self.user,name='Kale')
        Ingredient.objects.create(user=self.user,name='vanilla')
        
        res= self.client.get(INGREDIENR_URL)

        ingredients= Ingredient.objects.all().order_by('-name')
        serializer=IngredientSerializer(ingredients,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    
    def test_ingredients_limited_to_user(self):
        """Test list of ingredient limited to authenticated user"""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2,name='Salt')
        ingredient = Ingredient.objects.create(user=self.user,name='Pepper')

        res=self.client.get(INGREDIENR_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_updating_ingredient(self):
        """Test updating ingredient"""
        ingredient=Ingredient.objects.create(user=self.user,name='cilantro')
        payload={'name':'Coriander'}
        url=detail_url(ingredient.id)
        res =self.client.patch(url,payload)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name,payload['name'])


    def test_delete_ingredient(self):
        ingredient=Ingredient.objects.create(user=self.user,name='Lettuce')
        url=detail_url(ingredient.id)

        res= self.client.delete(url)

        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        ingredient=Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredient.exists())
