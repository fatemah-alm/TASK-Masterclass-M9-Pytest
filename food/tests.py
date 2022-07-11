from urllib import response
from django.http import HttpResponse
from typing import Callable
import pytest
import json
from food.models import Cuisine, Ingredient
from functools import partial
from graphene_django.utils.testing import graphql_query
from hypothesis import given
from hypothesis import strategies as st
@pytest.fixture
@pytest.mark.django_db
def cuisine() -> Cuisine:
    return Cuisine.objects.create(name='foo')


@pytest.mark.django_db
def test_cuisine_query(client_query:partial[graphql_query], cuisine: Cuisine) -> None:
    response = client_query(
        f"""
        query {{
            cuisine(cuisineId: {cuisine.id}) {{
                id
                name
                banner
            }}
        }}
        """
    )
    content = json.loads(response.content)
    assert 'errors' not in content

    data = content["data"]["cuisine"]
    assert data["name"] == cuisine.name
    assert data["banner"] == cuisine.banner

@pytest.fixture
@pytest.mark.django_db
def ingredient() -> Ingredient:
    return Ingredient.objects.create(name='foo', origin='bar')

@given(name=st.text, origin=st.text)
@pytest.mark.django_db
def test_create_ingredient(client_query:Callable[...,any], name: str, origin: str) -> None:
    response = client_query(
        """


mutation createIngredient($name: string!, $origin: string!){
  createIngredient(name: "string", origin: "string") {
    ingredient {
      id
      name
      origin
      
    }
  }
}

        """, 
        op_name="createIngredient",
        variables= {"id": ingredient.id, "name":ingredient.name, "origin":ingredient.origin},

    )
    content = response.json()
    assert "errors" not in content
    data = content["data"]["createIngredient"]
    assert data["status"]
    print(data,"EEEE")