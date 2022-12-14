"""
Serializers for recipe api
"""

from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    """ serialzers for Recipe app"""

    class Meta:
        model=Recipe
        fields=['id','title','time_minutes','price','link']
        read_only_fields=['id']
 

class RecipeDetailSerializer(RecipeSerializer):
    """
    serializers for Recipe detail.
    """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']