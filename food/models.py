from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=30)
    origin = models.CharField(max_length=30)

    def __str__(self) -> str:
        return str(self.name)


class Cuisine(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return str(self.name)


class Recipe(models.Model):
    name = models.CharField(max_length=30)
    steps = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, related_name="recipes")
    cuisine = models.ForeignKey(
        Cuisine, related_name="recipes", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return str(self.name)
