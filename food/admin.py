from django.contrib import admin

from food.models import Cuisine, Ingredient, Recipe


admin.site.register([Cuisine, Ingredient, Recipe])
