"""
View fro recipe APIs.
"""

from rest_framework import (viewsets,mixins)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (Recipe,Tag, Ingredient)
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for managing recipe APIs"""
    serializer_class=serializers.RecipeDetailSerializer
    queryset=Recipe.objects.all()
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]


    def get_queryset(self):
        """Retrive recipes for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action=='list':
            return serializers.RecipeSerializer
        return self.serializer_class    

    def perform_create(self, serializer):
        """Create new recipe"""
        serializer.save(user=self.request.user)
        #return super().perform_create(serializer)

class BaseRcipeAttrViewSet(mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Base viewset for recipes"""
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticate user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

class TagViewSet(BaseRcipeAttrViewSet):
    """Manage Tags in Database"""
    serializer_class=serializers.TagSerializer
    queryset=Tag.objects.all()
         

class IngrediantViewSet(BaseRcipeAttrViewSet):
    """manage ingredient in Database"""
    serializer_class=serializers.IngredientSerializer
    queryset=Ingredient.objects.all()
    

    