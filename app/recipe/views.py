"""
View for recipe APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (viewsets,mixins,status)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (Recipe,Tag, Ingredient)
from recipe import serializers

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tag',
                OpenApiTypes.STR,
                description='Comma seperated list of tag ids to filter'
    
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='comma seperated list of ingredients ids to filter'
            )
            
        ]
    )
)

class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for managing recipe APIs"""
    serializer_class=serializers.RecipeDetailSerializer
    queryset=Recipe.objects.all()
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def _params_to_int(self,qs):
        """Convert a list of strings to Integer """
        return [int(str_id) for str_id in qs.split(',')]
    
    
    def get_queryset(self):
        """Retrive recipes for authenticated user"""
        tags=self.request.query_params.get('tag')
        ingredients=self.request.query_params.get('ingredients')
        queryset=self.queryset

        if tags:
            tag_ids=self._params_to_int(tags)
            queryset=queryset.filter(tag__id__in=tag_ids)
        if ingredients:
            ingredient_ids=self._params_to_int(ingredients)
            queryset= queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.filter(
            user=self.request.user,
        ).order_by('-id').distinct()



    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class
       
         

    def perform_create(self, serializer):
        """Create new recipe"""
        serializer.save(user=self.request.user)
    
    @action(methods=['POST'],detail=True,url_path='upload_image')
    def upload_image(self,request,pk=None):
        """Upload an image to recipe."""
        recipe=self.get_object()
        serializer=self.get_serializer(recipe,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT,enum=[0,1],
                description='Filter by item assigned to recipe'
            )
        ]
    )
)
class BaseRcipeAttrViewSet(mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Base viewset for recipes"""
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticate user"""
        assigned_only =  bool(
            int(self.request.query_params.get('assigned_only',0))
        )
        queryset=self.queryset
        if assigned_only:
            queryset=queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
            ).order_by('-name').distinct()

class TagViewSet(BaseRcipeAttrViewSet):
    """Manage Tags in Database"""
    serializer_class=serializers.TagSerializer
    queryset=Tag.objects.all()
         

class IngrediantViewSet(BaseRcipeAttrViewSet):
    """manage ingredient in Database"""
    serializer_class=serializers.IngredientSerializer
    queryset=Ingredient.objects.all()
    

    