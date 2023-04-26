"""
Test for creating Ingredients
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Ingredient,Recipe)

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

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
        res= self.client.get(INGREDIENT_URL)

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
        
        res= self.client.get(INGREDIENT_URL)

        ingredients= Ingredient.objects.all().order_by('-name')
        serializer=IngredientSerializer(ingredients,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    
    def test_ingredients_limited_to_user(self):
        """Test list of ingredient limited to authenticated user"""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2,name='Salt')
        ingredient = Ingredient.objects.create(user=self.user,name='Pepper')

        res=self.client.get(INGREDIENT_URL)

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

    def test_filter_ingredients_assign_to_recipe(self):
        """Test filtering ingredients those assign to recipe"""
        in1= Ingredient.objects.create(user=self.user,name='Apple')
        in2=Ingredient.objects.create(user=self.user,name='Turkey')
        recipe=Recipe.objects.create(
            user=self.user,
            title='Apple crumble',
            price=Decimal('2.3'),
            time_minutes=5
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENT_URL,{'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)

        self.assertIn(s1.data,res.data)
        self.assertNotIn(s2.data,res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredient return unique list."""
        ing= Ingredient.objects.create(user= self.user,name='Egg')
        Ingredient.objects.create(user=self.user, name = 'Lentils')
        recipe1= Recipe.objects.create(
            user=self.user,
            title='Egg Benedict',
            price=Decimal('3.33'),
            time_minutes=30,
        )
        recipe2=Recipe.objects.create(
            user=self.user,
            title='Lentils Parker',
            price=Decimal('2.2'),
            time_minutes=20,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res= self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data),1)
