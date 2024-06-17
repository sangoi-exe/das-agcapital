import pytest
from ag_backend.schema import schema
from django.contrib.auth import get_user_model
from graphene.test import Client as GraphQLClient


@pytest.fixture
def superuser(db):
    User = get_user_model()
    return User.objects.create_superuser("root", "admin@example.com", "wasder")


@pytest.fixture
def graphql_client():
    return GraphQLClient(schema)


@pytest.fixture
def graphql_request():
    return GraphQLClient(schema)
