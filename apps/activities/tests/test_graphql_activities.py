import pytest
from base64 import b64decode
from datetime import date, timedelta

from ag_backend.schema import schema
from apps.projects.models import Project
from apps.activities.models import Activity

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from graphene.test import Client as GraphQLClient


@pytest.mark.django_db
class ActivityGraphQLTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username="cleiton", password="securepassword")
        self.project = Project.objects.create(
            owner=self.user,
            name="Sample Project",
            description="Sample Project Description",
            status="open",
            start_date=date.today(),
            estimated_end_date=date.today() + timedelta(days=30),
        )
        self.graphql_client = GraphQLClient(schema)
        self.request = RequestFactory().get("/")
        self.request.user = self.user
        self.activity_id = None

    def test_activity_lifecycle(self):
        create_query = f"""
            mutation {{
                createActivity(projectId: "{self.project.id}", name: "First Activity", description: "Test Activity", priority: "low", status: "pending", creationDate: "{date.today()}", expectedCompletionDate: "{date.today() + timedelta(days=30)}") {{
                    activity {{
                        id
                        projectId
                        name
                        description
                        priority
                        status
                        creationDate
                        expectedCompletionDate
                    }}
                    success
                    errors                    
                }}
            }}
        """

        response = self.graphql_client.execute(create_query, context_value={"user": self.user})

        if "errors" in response:
            print("Errors:", response["errors"])

        assert response["data"]["createActivity"]["success"] is True, "Mutation should succeed"

        encoded_id = response["data"]["createActivity"]["activity"]["id"]
        decoded_id = b64decode(encoded_id).decode("utf-8").split(":")[-1]

        self.activity_id = int(decoded_id)

        update_query = f"""
            mutation {{
                updateActivity(id: "{self.activity_id}", description: "Updated Activity", priority: "high") {{
                    activity {{
                        description
                        priority
                    }}
                    success
                    errors
                }}
            }}
        """

        response = self.graphql_client.execute(update_query, context_value={"user": self.user})

        if "errors" in response:
            print("Errors:", response["errors"])

        assert response["data"]["updateActivity"]["success"] is True, "Mutation should succeed"
        assert response["data"]["updateActivity"]["activity"]["description"] == "Updated Activity", "Description should be updated"
        assert response["data"]["updateActivity"]["activity"]["priority"] == "HIGH", "Priority should be updated"

        delete_query = f"""
            mutation {{
                deleteActivity(id: "{self.activity_id}") {{
                    success
                    errors
                }}
            }}
        """

        response = self.graphql_client.execute(delete_query, context_value={"user": self.user})

        if "errors" in response:
            print("Errors:", response["errors"])

        assert response["data"]["deleteActivity"]["success"] is True, "Mutation should succeed"

        with self.assertRaises(Activity.DoesNotExist):
            Activity.objects.get(pk=self.activity_id)

    def tearDown(self):
        get_user_model().objects.all().delete()
