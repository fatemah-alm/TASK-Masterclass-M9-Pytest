from typing import Any, Union

import graphene
import graphene_django
from django.db.models import QuerySet
from django.db.utils import IntegrityError
from graphql import GraphQLError

from food.models import Cuisine, Ingredient, Recipe
from food.types import (
    CuisineInputType,
    CuisineType,
    IngredientInputType,
    IngredientType,
    RecipeType,
)
from food.utils import get_case_insensitive_regex


class FoodQuery(graphene.ObjectType):
    # Fields
    recipe = graphene.Field(
        RecipeType, recipe_id=graphene.Int(), name=graphene.String()
    )
    ingredient = graphene.Field(
        RecipeType, ingredient_id=graphene.Int(required=True)
    )
    cuisine = graphene.Field(
        RecipeType, cuisine_id=graphene.Int(required=True)
    )

    # Lists
    recipes = graphene_django.DjangoListField(
        RecipeType,
        offset=graphene.Int(),
        limit=graphene.Int(),
        name=graphene.String(),
        cuisine=graphene.String(),
        ingredients=graphene.List(graphene.String),
    )
    ingredients = graphene_django.DjangoListField(
        IngredientType,
        offset=graphene.Int(),
        limit=graphene.Int(),
        name=graphene.String(),
        origin=graphene.String(),
        used_in=graphene.List(
            graphene.String,
            description=(
                "Search for a cuisine name that used these ingredients (e.g., "
                "Italian -> Tomato, Wheat, etc...)"
            ),
        ),
    )
    cuisines = graphene_django.DjangoListField(
        CuisineType,
        offset=graphene.Int(),
        limit=graphene.Int(),
        name=graphene.String(),
        recipes=graphene.List(graphene.String),
        ingredients=graphene.List(graphene.String),
    )

    def resolve_recipe(
        root,
        info: graphene.ResolveInfo,
        recipe_id: Union[int, None] = None,
        name: Union[str, None] = None,
    ) -> Recipe:
        if recipe_id is name is None:
            raise GraphQLError("must use either recipeId or name")

        lookup: dict[str, Any] = dict(id=recipe_id, name=name)

        try:
            return Recipe.objects.get(**lookup)
        except Recipe.DoesNotExist as exc:
            raise GraphQLError(str(exc))

    def resolve_ingredient(
        root, info: graphene.ResolveInfo, ingredient_id: int
    ) -> Ingredient:
        try:
            return Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist as exc:
            raise GraphQLError(str(exc))

    def resolve_cuisine(
        root, info: graphene.ResolveInfo, cuisine_id: int
    ) -> Cuisine:
        try:
            return Cuisine.objects.get(id=cuisine_id)
        except Cuisine.DoesNotExist as exc:
            raise GraphQLError(str(exc))

    def resolve_recipes(
        root,
        *info: graphene.ResolveInfo,
        offset: Union[int, None] = None,
        limit: Union[int, None] = None,
        name: Union[str, None] = None,
        cuisine: Union[str, None] = None,
        ingredients: Union[list[str], None] = None,
    ) -> QuerySet[Recipe]:
        q: dict[str, Any] = {}
        if name is not None:
            q.update(name__icontains=name)
        if cuisine is not None:
            q.update(cuisine__name__icontains=cuisine)
        if ingredients is not None:
            pat = get_case_insensitive_regex(ingredients)
            q.update(ingredients__name__iregex=pat)

        query = Recipe.objects.filter(**q)
        return query[slice(offset, limit)]

    def resolve_ingredients(
        root,
        *info: graphene.ResolveInfo,
        offset: Union[int, None] = None,
        limit: Union[int, None] = None,
        name: Union[str, None] = None,
        origin: Union[str, None] = None,
        used_in: Union[list[str], None] = None,
    ) -> QuerySet[Ingredient]:
        q: dict[str, Any] = {}
        if name is not None:
            q.update(name__icontains=name)
        if origin is not None:
            q.update(origin__name__icontains=origin)
        if used_in is not None:
            pat = get_case_insensitive_regex(used_in)
            q.update(recipes__cuisine__name__iregex=pat)

        query = Ingredient.objects.filter(**q)
        return query[slice(offset, limit)]

    def resolve_cuisines(
        root,
        *info: graphene.ResolveInfo,
        offset: Union[int, None] = None,
        limit: Union[int, None] = None,
        name: Union[str, None] = None,
        recipes: Union[list[str], None] = None,
        ingredients: Union[list[str], None] = None,
    ) -> QuerySet[Cuisine]:
        q: dict[str, Any] = {}
        if name is not None:
            q.update(name__icontains=name)
        if recipes is not None:
            pat = get_case_insensitive_regex(recipes)
            q.update(recipes__name__iregex=pat)
        if ingredients is not None:
            pat = get_case_insensitive_regex(ingredients)
            q.update(ingredients__name__iregex=pat)

        query = Cuisine.objects.filter(**q)
        return query[slice(offset, limit)]


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
