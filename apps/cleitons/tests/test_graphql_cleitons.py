import pytest
from graphene.test import Client
from ag_backend.schema import schema
from apps.cleitons.models import Cleiton
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory


@pytest.mark.django_db
class CleitonGraphQLTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.username = get_user_model().objects.create_user(username="admin", password="securepassword", is_staff=True)
        self.client = Client(schema)
        self.request = RequestFactory().get("/")
        self.request.user = self.username

    def test_create_cleiton(self):
        create_query = """
            mutation {
                createCleiton(username: "cleiton_user", name: "Cleiton Silva", email: "cleiton@example.com", phone: "1234567890", address: "123 Baker Street") {
                    cleiton {
                        id
                        username
                        name
                        email
                        phone
                        address
                    }
                    success
                    errors
                }
            }
        """
        response = self.client.execute(create_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        self.assertTrue(response["data"]["createCleiton"]["success"], "Mutation should succeed")
        self.assertIsNotNone(response["data"]["createCleiton"]["cleiton"], "Cleiton should be created")
        self.cleiton_id = response["data"]["createCleiton"]["cleiton"]["id"]

    def test_update_cleiton(self):
        cleiton = Cleiton.objects.create(username="cleiton_user", name="Cleiton Silva", email="cleiton@example.com")
        update_query = f"""
            mutation {{
                updateCleiton(id: "{cleiton.id}", username: "updated_cleiton_user", name: "Updated Cleiton Silva", phone: "9876543210") {{
                    cleiton {{
                        username
                        name
                        phone
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
        self.assertTrue(response["data"]["updateCleiton"]["success"], "Mutation should succeed")
        cleiton.refresh_from_db()
        self.assertEqual(cleiton.username, "updated_cleiton_user", "Username should be updated")
        self.assertEqual(cleiton.name, "Updated Cleiton Silva", "Name should be updated")
        self.assertEqual(cleiton.phone, "9876543210", "Phone should be updated")

    def test_delete_cleiton(self):
        cleiton = Cleiton.objects.create(username="cleiton_user", name="Cleiton Silva", email="cleiton@example.com")
        delete_query = f"""
            mutation {{
                deleteCleiton(id: "{cleiton.id}") {{
                    success
                    errors
                }}
            }}
        """
        response = self.client.execute(delete_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        self.assertTrue(response["data"]["deleteCleiton"]["success"], "Mutation should succeed")
        with self.assertRaises(Cleiton.DoesNotExist):
            Cleiton.objects.get(pk=cleiton.id)
