import pytest
from django.contrib.auth import get_user_model
from apps.activities.models import Activity
from apps.cleitons.models import Cleiton
from apps.projects.models import Project
from graphene.test import Client as GraphQLClient
from ag_backend.schema import schema


@pytest.fixture
def superuser(db):
    User = get_user_model()
    return User.objects.create_superuser("root", "admin@example.com", "wasder")


@pytest.fixture
def test_user(db):
    User = get_user_model()
    return User.objects.create_user("testuser", "test@example.com", "password123", is_staff=True)


@pytest.fixture
def graphql_request_superuser(client, superuser):
    client.force_login(superuser)
    return client


@pytest.fixture
def graphql_request_user(client, test_user):
    client.force_login(test_user)
    return client


@pytest.fixture
def test_cleiton(db):
    return Cleiton.objects.create(
        name="Test Client",
        email="cleiton@teste.com",
        phone="55999999999",
        address="Floripa",
    )


@pytest.fixture
def test_project(db, test_cleiton):
    return Project.objects.create(
        name="Test Project",
        description="A simple test project",
        cleiton=test_cleiton,
        status="open",
        start_date="2024-01-01",
        estimated_end_date="2024-12-31",
    )


@pytest.fixture
def test_activity(db, test_project):
    return Activity.objects.create(
        description="Initial Test Activity",
        project=test_project,
        priority="medium",
        status="pending",
        creation_date="2024-06-20",
        expected_completion_date="2024-07-20",
    )


@pytest.fixture
def graphql_client():
    return GraphQLClient(schema)
