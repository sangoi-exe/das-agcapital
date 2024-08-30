
from base64 import b64decode
from ag_backend.schema import schema
from django.contrib.auth import get_user_model
from graphene.test import Client as GraphQLClient
from django.test import TestCase, RequestFactory, Client as DjangoClient


class UserQueryGraphQLTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_superuser(username="root", password="wasder", email="admin@example.com")
        self.django_client = DjangoClient()
        self.graphql_client = GraphQLClient(schema)
        self.request = RequestFactory().get("/")
        self.request.user = self.user

        logged_in = self.django_client.login(username="root", password="wasder")
        assert logged_in, "Login failed"
        response = self.django_client.get("/admin/")
        assert response.status_code == 200, "Admin page should return status 200"

    def test_user_query(self):
        query = f"""
        {{
            user(id: "{self.user.id}") {{
                username
                email
            }}
        }}
        """
        executed = self.graphql_client.execute(query, context_value={"user": self.user})
        print(executed)
        if "errors" in executed:
            print("Errors:", executed["errors"])
        assert executed == {
            "data": {"user": {"username": "root", "email": "admin@example.com"}}
        }, "Query should return the correct user data"

    def test_create_user(self):
        create_query = """
            mutation {
                createAccountsUser(username: "newuser", password: "wasder", email: "new@example.com") {
                    accountsUser {
                        id
                        username
                        email
                    }
                    success
                    errors
                }
            }
        """
        response = self.graphql_client.execute(create_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["createAccountsUser"]["success"] is True, "Mutation should succeed"

        encoded_id = response["data"]["createAccountsUser"]["accountsUser"]["id"]
        decoded_id = b64decode(encoded_id).decode("utf-8").split(":")[-1]

        new_user = get_user_model().objects.get(pk=decoded_id)
        assert new_user.username == "newuser", "Username should be 'newuser'"
        assert new_user.email == "new@example.com", "Email should be 'new@example.com'"

    def test_update_user(self):
        new_user = get_user_model().objects.create_user(username="newuser", password="wasder", email="new@example.com")
        update_query = f"""
            mutation {{
                updateAccountsUser(id: "{new_user.id}", email: "updated@example.com") {{
                    accountsUser {{
                        username
                        email
                    }}
                    success
                    errors
                }}
            }}
        """
        response = self.graphql_client.execute(update_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["updateAccountsUser"]["success"] is True, "Mutation should succeed"
        new_user.refresh_from_db()
        assert new_user.email == "updated@example.com", "Email should be updated to 'updated@example.com'"

    def test_delete_user(self):
        new_user = get_user_model().objects.create_user(username="newuser", password="wasder", email="new@example.com")
        delete_query = f"""
            mutation {{
                deleteAccountsUser(id: "{new_user.id}") {{
                    success
                    errors
                }}
            }}
        """
        response = self.graphql_client.execute(delete_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["deleteAccountsUser"]["success"] is True, "Mutation should succeed"
        with self.assertRaises(get_user_model().DoesNotExist):
            get_user_model().objects.get(pk=new_user.id)
