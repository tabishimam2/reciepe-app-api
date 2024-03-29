"""
Test for recipe APIs
"""

from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list') 

def detail_url(recipe_id):
    """Create and return a recipe URL"""
    return reverse('recipe:recipe-detail',args=[recipe_id])


def image_upload_url(recipe_id):
    """Create and return a image upload URL"""
    return reverse('recipe:recipe-upload-image',args=[recipe_id])


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
       # self.assertEqual(res.data,serializer.data)

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

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with  tag."""

        payload={
            'title':'Thai Prawn Curry',
            'price': Decimal(3.39),
            'time_minutes':30,
            'tag':[{'name':'Thai'},{'name':'Dinner'}]
        }

        res = self.client.post(RECIPES_URL,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(),2)
        for tags in payload['tag']:
            exists= recipe.tag.filter(
                name=tags['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_creating_recipe_with_existing_tags(self):
        """Test creating recipe with existing tag."""
        tag_indian= Tag.objects.create(user=self.user,name='Indian')
        payload= {
            'title': 'Chicken Masala',
            'time_minutes':30,
            'price':Decimal(2.59),
            'tag':[{'name':'Indian'},{'name':'Breakfast'}]
        }

        res = self.client.post(RECIPES_URL,payload,format='json')
        
        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(),2)
        self.assertIn(tag_indian,recipe.tag.all())
        for tags in payload['tag']:
            exists= recipe.tag.filter(
                name=tags['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_updaet(self):
        """Test creating tag on updating a recipe"""
        recipe=create_recipe(user=self.user)
        payload={'tag':[{'name':'Lunch'}]}
        url=detail_url(recipe.id)
        res=self.client.patch(url,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        new_tag=Tag.objects.get(user=self.user,name='Lunch')
        self.assertIn(new_tag,recipe.tag.all())

    def test_update_recipe_assign_tag(self):
        """Test asssigning existing tag on updating a recipe"""

        tag_breakfast=Tag.objects.create(user=self.user,name='Breakfast')
        recipe=create_recipe(user=self.user)
        recipe.tag.add(tag_breakfast)

        tag_lunch= Tag.objects.create(user=self.user,name='Lunch')
        payload={'tag':[{'name':'Lunch'}]}
        url=detail_url(recipe.id)
        res=self.client.patch(url,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(tag_lunch,recipe.tag.all())
        self.assertNotIn(tag_breakfast,recipe.tag.all())

    def test_clear_recipe_tags(self):
        """Test clearing the tags"""
        tag=Tag.objects.create(user=self.user,name='Dessert')
        recipe=create_recipe(user=self.user)
        recipe.tag.add(tag)

        payload={'tag':[]}
        url=detail_url(recipe.id)
        res=self.client.patch(url,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(recipe.tag.count(),0)


    def test_create_recipe_with_new_ingredient(self):
        """Test creating recipe with new ingredients """
        payload={
            'title':'Cauliflower tacos',
            'time_minutes':30,
            'price':Decimal('2.50'),
            'ingredients': [{'name':'Cauliflower'},{'name':'Salt'}],
        }
        res= self.client.post(RECIPES_URL,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe=recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)
        for ingredient in payload['ingredients']:
            exists=recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_creating_recipe_with_existing_ingredient(self):
        """Test creating recipe with existing ingredient"""
        ingredient=Ingredient.objects.create(user=self.user,name='Lemon')
        payload={
            'title':'Vietnamess soup',
            'price':Decimal('2.23'),
            'time_minutes':23,
            'ingredients':[{'name':'Lemon'},{'name':'Fish Sauce'}]
        }
        res = self.client.post(RECIPES_URL,payload,format='json')


        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        recipes=Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe=recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)
        self.assertIn(ingredient,recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            exists=recipe.ingredients.filter(
                user=self.user,
                name=ingredient['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient when updating a recipe """
        recipe= create_recipe(user=self.user)
        url=detail_url(recipe.id)
        payload= {'ingredients':[{'name':'Limes'}]}

        res = self.client.patch(url,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        new_ingredient=Ingredient.objects.get(user=self.user,name='Limes')
        self.assertIn(new_ingredient,recipe.ingredients.all())

    def test_update_recipe_assing_ingredients(self):
        ingredient1= Ingredient.objects.create(user=self.user,name='Pepper')
        recipe=create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2= Ingredient.objects.create(user=self.user,name='Chili')
        payload={'ingredients':[{'name':'Chili'}]}
        url =detail_url(recipe.id)
        res = self.client.patch(url,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn(ingredient2,recipe.ingredients.all())
        self.assertNotIn(ingredient1,recipe.ingredients.all())

    def test_clear_recipe_ingredient(self):
        ingredient=Ingredient.objects.create(user=self.user,name='Garlic')
        recipe= create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload={'ingredients':[]}
        url=detail_url(recipe.id)
        res = self.client.patch(url,payload,format='json')

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(),0)

    def test_filtre_by_tags(self):
        """Test filtering recipes using tags."""
        r1= create_recipe(user=self.user,title='Thai vegetable curry')
        r2= create_recipe(user=self.user,title='Eggplant with Tahini')
        
        tag1=Tag.objects.create(user=self.user, name='Vegan')
        tag2=Tag.objects.create(user=self.user,name='Vegetarian')
        r1.tag.add(tag1)
        r2.tag.add(tag2)
        r3 = create_recipe(user=self.user,title='fish curry chips')

        params= {'tag':f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPES_URL,params)

        s1=RecipeSerializer(r1)
        s2=RecipeSerializer(r2)
        s3=RecipeSerializer(r3)

        self.assertIn(s1.data,res.data)
        self.assertIn(s2.data,res.data)
        self.assertNotIn(s3.data,res.data)

    def test_filter_by_ingredients(self):
        """Test filtering recipes using ingredients."""
        r1= create_recipe(user=self.user,title='Paosh Beans')
        r2= create_recipe(user=self.user,title='Chicken caccitore')
        in1=Ingredient.objects.create(user=self.user,name='Feta Cheese')
        in2= Ingredient.objects.create(user=self.user,name='Chicken')

        r1.ingredients.add(in1)
        r2.ingredients.add(in2)
        r3 = create_recipe(user=self.user,title='albertoo')
        params= {'ingredients':f'{in1.id},{in2.id}'}
        res = self.client.get(RECIPES_URL,params)

        s1=RecipeSerializer(r1)
        s2=RecipeSerializer(r2)
        s3=RecipeSerializer(r3)

        self.assertIn(s1.data,res.data)
        self.assertIn(s2.data,res.data)
        self.assertNotIn(s3.data,res.data)




class IMageUploadTest(TestCase):
    """Test for image upload API"""

    def setUp(self):
        self.client=APIClient()
        self.user=get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)
        self.recipe= create_recipe(user=self.user)


    def teardown(self):
        self.recipe.image.delete()

    def Test_upload_image(self):
        """test for uploading image to a recipe"""
        url=image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img= Image.new('RGB',(10,10))
            img.save(image_file,format='JPEG')
            image_file.seek(0)
            payload = {'image':image_file}
            res = self.client.post(url,payload,format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertIn('image',res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))


    def test_upload_bad_image(self):
        """Test uploading invalid image"""
        url = image_upload_url(self.recipe.id)
        payload= {'image':'notanimage'}
        res=self.client.post(url,payload,format='multipart')

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
