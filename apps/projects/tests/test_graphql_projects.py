import pytest
from apps.projects.models import Project
from base64 import b64decode
from ag_backend.schema import schema
from django.contrib.auth import get_user_model
from graphene.test import Client as GraphQLClient
from django.test import TestCase, RequestFactory, Client as DjangoClient


@pytest.mark.django_db
class ProjectGraphQLTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username="admin", password="safe_password", email="admin@example.com")
        self.graphql_client = GraphQLClient(schema)
        self.request = RequestFactory().get("/")
        self.request.user = self.user
        self.project_id = None

    def test_create_project(self):
        create_project_query = """
        mutation {
            createProject(owner: "admin", name: "New Project", description: "A test project.", status: "open", startDate: "2023-01-01", estimatedEndDate: "2023-12-31") {
                project {
                    id
                    name
                    description
                    status
                }
                success
                errors
            }
        }
        """
        response = self.graphql_client.execute(create_project_query, context_value={"user": self.user})
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["createProject"]["success"] is True, "Mutation should succeed"
        print("--------------------------------------------------")
        print(response["data"])
        print("--------------------------------------------------")
        encoded_id = response["data"]["createProject"]["project"]["id"]
        decoded_id = b64decode(encoded_id).decode("utf-8").split(":")[-1]

        self.project_id = int(decoded_id)


        update_project_query = f"""
        mutation {{
            updateProject(id: "{self.project_id}", name: "Updated Project") {{
                project {{
                    name
                }}
                success
                errors
            }}
        }}
        """
        response = self.graphql_client.execute(update_project_query, context_value={"user": self.user})
        if "errors" in response:
            print("Errors:", response["errors"])
        print("--------------------------------------------------")
        print(response["data"])
        print("--------------------------------------------------")
        assert response["data"]["updateProject"]["success"] is True, "Should successfully update a project"
        assert response["data"]["updateProject"]["project"]["name"] == "Updated Project", "Project name should be updated"

        delete_project_query = f"""
        mutation {{
            deleteProject(id: "{self.project_id}") {{
                success
                errors
            }}
        }}
        """
        response = self.graphql_client.execute(delete_project_query, context_value={"user": self.user})
        if "errors" in response:
            print("Errors:", response["errors"])
        print("--------------------------------------------------")
        print(response["data"])
        print("--------------------------------------------------")
        assert response["data"]["deleteProject"]["success"] is True, "Should successfully delete the project"

    def tearDown(self):
        get_user_model().objects.all().delete()
