import pytest
from graphene_django.utils.testing import graphql_query

import json

@pytest.fixture
def client_query(client):
    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client)

    return func

