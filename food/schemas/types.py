import graphene
import graphene_django

from food.models import Cuisine, Ingredient, Recipe


class IngredientType(graphene_django.DjangoObjectType):
    class Meta:
        model = Ingredient


class CuisineType(graphene_django.DjangoObjectType):
    class Meta:
        model = Cuisine


class RecipeType(graphene_django.DjangoObjectType):
    class Meta:
        model = Recipe


class IngredientInputType(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
    origin = graphene.String()


class CuisineInputType(graphene.InputObjectType):
    id = graphene.Int()
    name = graphene.String()
