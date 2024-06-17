from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from graphene.test import Client
from ag_backend.schema import schema
from apps.projects.models import Project
from apps.activities.models import Activity
from apps.cleitons.models import Cleiton
from datetime import date, timedelta


class ActivityGraphQLTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="root", password="wasder")
        self.cleiton = Cleiton.objects.create(
            name=self.user.username,
            email=f"{self.user.username}@example.com",
        )
        self.project = Project.objects.create(
            name="Sample Project",
            description="Sample Project Description",
            cleiton=self.cleiton,
            status="open",
            start_date=date.today(),
            estimated_end_date=date.today() + timedelta(days=30),
        )
        self.client = Client(schema)
        self.request = RequestFactory().get("/")
        self.request.user = self.user

    def test_create_activity(self):
        create_query = f"""
            mutation {{
                createActivity(description: "Test Activity", projectId: "{self.project.id}", priority: "high", status: "pending", creationDate: "{date.today()}", expectedCompletionDate: "{date.today() + timedelta(days=30)}") {{
                    activity {{
                        description
                        priority
                    }}
                    success
                }}
            }}
        """
        response = self.client.execute(create_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["createActivity"]["success"] is True, "Mutation should succeed"
