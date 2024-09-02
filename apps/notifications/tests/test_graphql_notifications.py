from graphene.test import Client
from datetime import date, timedelta
from ag_backend.schema import schema
from apps.projects.models import Project
from apps.notifications.models import Notification
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from base64 import b64decode


class NotificationGraphQLTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username="cleiton", password="securepassword")
        self.cleiton = Cleiton.objects.create(
            user=self.user,
            name="Cleiton",
            email=f"{self.user}@example.com",
        )
        self.project = Project.objects.create(
            name="Sample Project",
            description="Sample Project Description",
            cleiton=self.cleiton,
            status="open",
            start_date=date.today(),
            estimated_end_date=date.today() + timedelta(days=30),
        )
        self.notification = Notification.objects.create(
            cleiton=self.cleiton,
            title="Test Notification",
            message="This is a test notification.",
            project=self.project,
        )
        self.client = Client(schema)
        self.request = RequestFactory().get("/")
        self.request.user = self.user

    def test_create_notification(self):
        create_query = f"""
            mutation {{
                createNotification(
                    cleitonId: "{self.cleiton.id}", 
                    title: "Test Notification", 
                    message: "This is a test notification.", 
                    projectId: "{self.project.id}") {{
                    notification {{
                        id
                        title
                        message
                        read
                    }}
                    success
                    errors
                }}
            }}
        """
        response = self.client.execute(create_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        self.assertTrue(response["data"]["createNotification"]["success"], "Mutation should succeed")
        self.assertIsNotNone(response["data"]["createNotification"]["notification"], "Notification should be created")

        encoded_id = response["data"]["createNotification"]["notification"]["id"]
        decoded_id = b64decode(encoded_id).decode("utf-8").split(":")[-1]
        self.notification_id = decoded_id

    def test_update_notification(self):
        update_query = f"""
            mutation {{
                updateNotification(id: "{self.notification.id}", title: "Updated Title", message: "Updated Message") {{
                    notification {{
                        id
                        title
                        message
                    }}
                    success
                    errors
                }}
            }}
        """
        response = self.client.execute(update_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        self.assertTrue(response["data"]["updateNotification"]["success"], "Mutation should succeed")
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.title, "Updated Title", "Title should be updated")
        self.assertEqual(self.notification.message, "Updated Message", "Message should be updated")

    def test_delete_notification(self):
        delete_query = f"""
            mutation {{
                deleteNotification(id: "{self.notification.id}") {{
                    success
                    errors
                }}
            }}
        """
        response = self.client.execute(delete_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        self.assertTrue(response["data"]["deleteNotification"]["success"], "Mutation should succeed")
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(pk=self.notification.id)
