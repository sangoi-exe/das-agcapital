from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from graphene.test import Client
from ag_backend.schema import schema
from apps.projects.models import Project
from apps.cleitons.models import Cleiton
from datetime import date, timedelta
from apps.activities.models import Activity


class ActivityGraphQLTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username="cleiton", password="securepassword")
        print(self.user)
        self.cleiton = Cleiton.objects.create(
            user=self.user,
            name="Cleiton",
            email=f"{self.user}@example.com",
        )
        print(self.cleiton.user)
        self.project = Project.objects.create(
            name="Sample Project",
            description="Sample Project Description",
            cleiton=self.cleiton,
            status="open",
            start_date=date.today(),
            estimated_end_date=date.today() + timedelta(days=30),
        )
        self.activity = Activity.objects.create(
            description="Initial Activity",
            project=self.project,
            priority="medium",
            status="pending",
            creation_date=date.today(),
            expected_completion_date=date.today() + timedelta(days=10),
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

    def test_update_activity(self):
        update_query = f"""
            mutation {{
                updateActivity(id: "{self.activity.id}", description: "Updated Activity", priority: "high") {{
                    activity {{
                        description
                        priority
                    }}
                    success
                }}
            }}
        """
        response = self.client.execute(update_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["updateActivity"]["success"] is True, "Mutation should succeed"
        self.activity.refresh_from_db()
        assert self.activity.description == "Updated Activity", "Description should be updated"
        assert self.activity.priority == "high", "Priority should be updated"

    def test_delete_activity(self):
        delete_query = f"""
            mutation {{
                deleteActivity(id: "{self.activity.id}") {{
                    success
                }}
            }}
        """
        response = self.client.execute(delete_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["deleteActivity"]["success"] is True, "Mutation should succeed"
        with self.assertRaises(Activity.DoesNotExist):
            Activity.objects.get(pk=self.activity.id)
