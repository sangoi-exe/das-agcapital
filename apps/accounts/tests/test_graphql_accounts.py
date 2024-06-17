import pytest
from graphene.test import Client as GraphQLClient
from django.test import Client as DjangoClient
from base64 import b64decode
from ag_backend.schema import schema


@pytest.mark.django_db
def test_user_query(superuser):
    client = GraphQLClient(schema)
    executed = client.execute("""{ user(id: "%s") { username, email } }""" % superuser.id)
    assert executed == {"data": {"user": {"username": "root", "email": "admin@example.com"}}}


@pytest.mark.django_db
def test_create_update_delete_user(superuser, graphql_request):
    django_client = DjangoClient()
    logged_in = django_client.login(username="root", password="wasder")
    assert logged_in, "Login failed"

    response = django_client.get("/admin/")
    print(f"/admin/ response status code: {response.status_code}")

    csrf_token = django_client.cookies["csrftoken"].value

    graphql_client = GraphQLClient(schema)

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
    create_executed = graphql_client.execute(create_query, context_value=graphql_request)

    print("create:", create_executed)
    assert create_executed["data"]["createAccountsUser"]["success"] is True, create_executed["data"]["createAccountsUser"]["errors"]
    encoded_id = create_executed["data"]["createAccountsUser"]["accountsUser"]["id"]
    decoded_id = b64decode(encoded_id).decode("utf-8").split(":")[-1]

    update_query = f"""
        mutation {{
            updateAccountsUser(id: "{decoded_id}", email: "updated@example.com") {{
                accountsUser {{
                    username
                    email
                }}
                success
                errors
            }}
        }}
    """
    update_executed = graphql_client.execute(update_query, context_value=graphql_request)
    print("update:", update_executed)
    assert update_executed["data"]["updateAccountsUser"]["success"] is True, update_executed["data"]["updateAccountsUser"]["errors"]
    assert update_executed["data"]["updateAccountsUser"]["accountsUser"]["email"] == "updated@example.com"

    delete_query = f"""
        mutation {{
            deleteAccountsUser(id: "{decoded_id}") {{
                success
                errors
            }}
        }}
    """
    delete_executed = graphql_client.execute(delete_query, context_value=graphql_request)
    print("delete:", delete_executed)
    assert delete_executed["data"]["deleteAccountsUser"]["success"] is True, delete_executed["data"]["deleteAccountsUser"]["errors"]
