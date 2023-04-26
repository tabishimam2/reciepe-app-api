"""
Serializers for recipe api
"""

from rest_framework import serializers

from core.models import (Recipe,Tag, Ingredient)

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient"""
    class Meta:
        model=Ingredient
        fields=['id','name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model=Tag
        fields = ['id','name']
        read_only_fields = ['id']
    

class RecipeSerializer(serializers.ModelSerializer):
    """ serialzers for Recipe app"""
    tag =TagSerializer(many=True, required=False)
    ingredients=IngredientSerializer(many=True,required=False)
    class Meta:
        model=Recipe
        fields=[
            'id','title','time_minutes','price','link','tag',
            'ingredients',
        ]
        read_only_fields=['id']
    def _get_or_create_tag(self,tag,recipe):
        """Handle getting or creating tags as needed"""
        auth_user=self.context['request'].user
        for tags in tag:
            tag_obj,create = Tag.objects.get_or_create(
                user=auth_user,
                **tags,
            )
            recipe.tag.add(tag_obj)
    
    def _get_or_create_ingredients(self,ingredietns,recipe):
        """Handle getting or creating ingredients as needed"""
        auth_user= self.context['request'].user
        for ingredient in ingredietns:
            ingredient_obj,create = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self,validated_data):
        """Create a recipe"""
        tag = validated_data.pop('tag',[])
        ingredients = validated_data.pop('ingredients',[])
        recipe=Recipe.objects.create(**validated_data)
        self._get_or_create_tag(tag,recipe)
        self._get_or_create_ingredients(ingredients,recipe)
        return recipe

    def update(self,instance,validated_data):
        """Updating recipe"""
        tag = validated_data.pop('tag',None)
        ingredients= validated_data.pop('ingredients',None)
        if tag is not None:
            instance.tag.clear()
            self._get_or_create_tag(tag,instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients,instance)
            
        for attr,value in validated_data.items():
            setattr(instance,attr,value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """
    serializers for Recipe detail.
    """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description' ,'image']



class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializers for uploading Image to recipe """

    class Meta:
        model=Recipe
        fields=['id','image']
        read_only_fields= ['id']
        extra_kwargs={'image':{'required':'True'}}




