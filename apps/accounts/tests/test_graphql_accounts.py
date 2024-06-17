import pytest
from django.contrib.auth import get_user_model
from graphene.test import Client
from base64 import b64decode

from ag_backend.schema import schema


@pytest.fixture
def user():
    User = get_user_model()
    return User.objects.create_user(username="testuser", email="test@example.com", password="securepassword")


@pytest.mark.django_db
def test_user_query(user):
    client = Client(schema)
    executed = client.execute("""{ user(id: "%s") { username, email } }""" % user.id)
    assert executed == {"data": {"user": {"username": "testuser", "email": "test@example.com"}}}


@pytest.mark.django_db
def test_create_update_delete_user():
    client = Client(schema)
    # Create user
    create_query = """
        mutation {
            createAccountsUser(username: "newuser", password: "wasder", email: "new@example.com") {
                accountsUser {
                    id
                    username
                    email
                }
                success
            }
        }
    """
    create_executed = client.execute(create_query)
    print("create:", create_executed)
    assert create_executed["data"]["createAccountsUser"]["success"] is True
    encoded_id = create_executed["data"]["createAccountsUser"]["accountsUser"]["id"]
    decoded_id = b64decode(encoded_id).decode("utf-8").split(":")[-1]

    # Update user
    update_query = f"""
        mutation {{
            updateAccountsUser(id: "{decoded_id}", email: "updated@example.com") {{
                accountsUser {{
                    username
                    email
                }}
                success
            }}
        }}
    """
    update_executed = client.execute(update_query)
    print("update:", update_executed)
    assert update_executed["data"]["updateAccountsUser"]["success"] is True
    assert update_executed["data"]["updateAccountsUser"]["accountsUser"]["email"] == "updated@example.com"

    # Delete user
    delete_query = f"""
        mutation {{
            deleteAccountsUser(id: "{decoded_id}") {{
                success
            }}
        }}
    """
    delete_executed = client.execute(delete_query)
    print("delete:", delete_executed)
    assert delete_executed["data"]["deleteAccountsUser"]["success"] is True
