"""
Serializers for recipe api
"""

from rest_framework import serializers

from core.models import (Recipe,Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model=Tag
        fields = ['id','name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):
    """ serialzers for Recipe app"""
    tag =TagSerializer(many=True, required=False)
    class Meta:
        model=Recipe
        fields=['id','title','time_minutes','price','link','tag']
        read_only_fields=['id']

    def create(self,validated_data):
        """Create a recipe"""
        tag = validated_data.pop('tag',[])
        recipe=Recipe.objects.create(**validated_data)
        auth_user=self.context['request'].user
        for tags in tag:
            tag_obj,created = Tag.objects.get_or_create(
                user=auth_user,
                **tags,
            )
            recipe.tag.add(tag_obj)
        return recipe
 

class RecipeDetailSerializer(RecipeSerializer):
    """
    serializers for Recipe detail.
    """
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']



