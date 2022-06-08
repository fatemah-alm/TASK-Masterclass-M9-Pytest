from typing import Any, Union

import graphene
from django.db.utils import IntegrityError
from graphql import GraphQLError

from food.models import Cuisine, Ingredient, Recipe
from food.schemas.types import (
    CuisineInputType,
    CuisineType,
    IngredientInputType,
    IngredientType,
    RecipeType,
)


class CreateIngredient(graphene.Mutation):
    ingredient = graphene.Field(IngredientType)

    class Arguments:
        name = graphene.String(required=True)
        origin = graphene.String(required=True)

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "CreateIngredient":
        ingredient = Ingredient.objects.create(**kwargs)
        return CreateIngredient(ingredient=ingredient)


class UpdateIngredient(graphene.Mutation):
    ingredient = graphene.Field(IngredientType)

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        origin = graphene.String()

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "UpdateIngredient":
        try:
            ingredient = Ingredient.objects.get(id=kwargs.pop("id"))
        except Ingredient.DoesNotExist:
            raise GraphQLError("could not find ingredient")

        for attr, value in kwargs.items():
            setattr(ingredient, attr, value)

        ingredient.save()

        return UpdateIngredient(ingredient=ingredient)


class DeleteIngredient(graphene.Mutation):
    status = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "DeleteRecipe":
        try:
            ingredient = Ingredient.objects.get(**kwargs)
        except Ingredient.DoesNotExist:
            return DeleteIngredient(status=False)

        ingredient.delete()
        return DeleteIngredient(status=True)


class CreateCuisine(graphene.Mutation):
    cuisine = graphene.Field(CuisineType)

    class Arguments:
        name = graphene.String(required=True)

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "CreateCuisine":
        cuisine = Cuisine.objects.create(**kwargs)
        return CreateCuisine(cuisine=cuisine)


class UpdateCuisine(graphene.Mutation):
    cuisine = graphene.Field(CuisineType)

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "UpdateCuisine":
        try:
            cuisine = Cuisine.objects.get(id=kwargs.pop("id"))
        except Cuisine.DoesNotExist:
            raise GraphQLError("could not find cuisine")

        for attr, value in kwargs.items():
            setattr(cuisine, attr, value)

        cuisine.save()

        return UpdateCuisine(cuisine=cuisine)


class DeleteCuisine(graphene.Mutation):
    status = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "DeleteCuisine":
        try:
            cuisine = Cuisine.objects.get(**kwargs)
        except Cuisine.DoesNotExist:
            return DeleteCuisine(status=False)

        cuisine.delete()
        return DeleteCuisine(status=True)


class CreateRecipe(graphene.Mutation):
    recipe = graphene.Field(RecipeType)

    class Arguments:
        name = graphene.String(required=True)
        steps = graphene.String(required=True)
        ingredients = graphene.List(
            IngredientInputType,
            description=(
                "Use ID to reference a created object, otherwise input the "
                "other fields"
            ),
        )
        cuisine = graphene.Argument(
            CuisineInputType,
            description=(
                "Use ID to reference a created object, otherwise input the "
                "other fields"
            ),
            required=True,
        )

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "CreateRecipe":
        ingredients = kwargs.pop("ingredients", [])
        cuisine = kwargs.pop("cuisine")
        if not cuisine:
            raise GraphQLError("cuisine cannot be empty")

        cuisine_db: Cuisine
        try:
            cuisine_db, _ = Cuisine.objects.get_or_create(**cuisine)
        except IntegrityError:
            raise GraphQLError("invalid cuisine object")

        ingredients_db: list[Ingredient] = []
        try:
            for ingredient in ingredients:
                ingredient_db, _ = Ingredient.objects.get_or_create(
                    **ingredient
                )
                ingredients_db.append(ingredient_db)
        except IntegrityError:
            cuisine_db.delete()
            Ingredient.objects.filter(id__in=ingredients_db).delete()
            raise GraphQLError("invalid ingredient object")

        recipe = Recipe.objects.create(cuisine=cuisine_db, **kwargs)
        recipe.ingredients.add(*ingredients_db)

        return CreateRecipe(recipe=recipe)


class UpdateRecipe(graphene.Mutation):
    recipe = graphene.Field(RecipeType)

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        steps = graphene.String()
        ingredients = graphene.List(graphene.Int)
        cuisine = graphene.Int()

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "UpdateRecipe":
        ingredients: Union[list[Any], None] = kwargs.pop("ingredients", None)

        try:
            recipe = Recipe.objects.get(id=kwargs.pop("id"))
        except Recipe.DoesNotExist:
            raise GraphQLError("could not find recipe")

        for attr, value in kwargs.items():
            setattr(recipe, attr, value)

        if ingredients:
            recipe.ingredients.clear()
            recipe.ingredients.add(*ingredients)

        return UpdateRecipe(recipe=recipe)


class DeleteRecipe(graphene.Mutation):
    status = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(
        root, info: graphene.ResolveInfo, **kwargs: Any
    ) -> "DeleteRecipe":
        try:
            recipe = Recipe.objects.get(**kwargs)
        except Recipe.DoesNotExist:
            return DeleteRecipe(status=False)

        recipe.delete()
        return DeleteRecipe(status=True)


class FoodMutation(graphene.ObjectType):
    # Ingredients
    create_ingredient = CreateIngredient.Field()
    update_ingredient = UpdateIngredient.Field()
    delete_ingredient = DeleteIngredient.Field()

    # Cuisines
    create_cuisine = CreateCuisine.Field()
    update_cuisine = UpdateCuisine.Field()
    delete_cuisine = DeleteCuisine.Field()

    # Recipes
    create_recipe = CreateRecipe.Field()
    update_recipe = UpdateRecipe.Field()
    delete_recipe = DeleteRecipe.Field()
