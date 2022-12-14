"""
Test for recipe APIs
"""

from decimal import Decimal
from email.policy import default
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list') 

def detail_url(recipe_id):
    """Create and return a recipe URL"""
    return reverse('recipe:recipe-detail',args=[recipe_id])


def create_recipe(user,**params):
    """ Create and return sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes':22 ,
        'description':'Sample description',
        'price': Decimal('5.25'),
        'link' : 'http://example.com/recipe.pdf',

    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)

class PublicRecipeAPITest(TestCase):
    """ Test the unauthenticate api request"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITest(TestCase):
    """Test authenciated API request."""
    def setUp(self) :
        self.client = APIClient()
        self.user=create_user(email='user@example.com',password='test123')
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrieve a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many = True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes limited to user"""
        other_user=create_user(email='other@example.com',password='test123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes,many = True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)


    def test_get_recipe_detail(self):
        """Test to get recipe details"""
        recipe = create_recipe(user=self.user)

        url=detail_url(recipe.id)
        res=self.client.get(url)

        serializer = RecipeDetailSerializer
        self.assertEqual(res.data,serializer.data)

    def test_create_recipe(self):
        """Test to check recipe creation through API"""
        payload={
            'title':'Sample Recipe',
            'time_minutes': 30,
            'price':Decimal('5.99')
        }
        res = self.client.post(RECIPES_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe=Recipe.objects.get(id=res.data['id'])
        for k,v in payload.items():
            self.assertEqual(getattr(recipe , k),v)
        self.assertEqual(recipe.user,self.user)

    def test_partial_updates(self):
        """Test partial updates on recipe"""
        original_link='https://example.com/recipe.pdf'
        recipe=create_recipe(
        user= self.user,
        title='Sample Recipe',
        link=original_link
        )

        payload={'title':"New Sample recipe"}
        url=detail_url(recipe.id)
        res = self.client.patch(url,payload)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(recipe.link,original_link)
        self.assertEqual(recipe.user,self.user)

    def test_full_update(self):
        """Test the full updates of the recipe"""
        recipe=create_recipe(
            user=self.user,
            title='Sample recipe',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description.'
        )
        payload={
            'title':'New Sample recipe',
            'link':'https://example.com/new-recipe.pdf',
            'description':'New sample recipe description',
            'time_minutes':33,
            'price':Decimal('2.33'),
        }
        url=detail_url(recipe.id)
        res=self.client.put(url,payload)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(getattr(recipe,k),v)
        self.assertEqual(recipe.user,self.user)


    def test_update_user_return_error(self):
        """Test changing recipe user results in error"""
        new_user=create_user(email='user2@example.com',password='test123')
        recipe=create_recipe(user=self.user)

        payload={'user':new_user.id}
        url=detail_url(recipe.id)
        self.client.patch(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user,self.user)

    def test_delete_recipe(self):
        """test deleting recipe"""
        recipe=create_recipe(user=self.user)
        url=detail_url(recipe.id)

        res=self.client.delete(url)
        self.assertEqual(res.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())


    def test_delete_other_user_recipe_return_eeror(self):
        new_user=create_user(email='user2@example.com',password='test@123')
        recipe=create_recipe(user=new_user)

        url=detail_url(recipe.id)
        res=self.client.delete(url)

        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())