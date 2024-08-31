from graphene.test import Client
from ag_backend.schema import schema
from datetime import date, timedelta
from apps.projects.models import Project
from apps.cleitons.models import Cleiton
from apps.documents.models import Document
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory


class DocumentGraphQLTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username="cleiton", password="securepassword")
        self.cleiton = Cleiton.objects.create(
            username=self.user.username,
            name="Cleiton",
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
        self.document = Document.objects.create(
            name="Project Document",
            file="Document.pdf",
            project=self.project,
            uploaded_at=date.today(),
        )
        self.client = Client(schema)
        self.request = RequestFactory().get("/")
        self.request.user = self.user

    def test_create_document(self):
        create_query = f"""
            mutation {{
                createDocument(name: "{self.document.name}", file: "{self.document.file}", projectId: "{self.project.id}", uploadedAt: "{date.today()}") {{
                    document {{
                        name
                        file                        
                    }}
                    success
                }}
            }}
        """
        response = self.client.execute(create_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["createDocument"]["success"] is True, "Mutation should succeed"

    def test_update_document(self):
        update_query = f"""
            mutation {{
                updateDocument(id: "{self.document.id}", name: "Updated Document", file: "Updated file") {{
                    document {{
                        name
                        file                        
                    }}
                    success
                }}
            }}
        """
        response = self.client.execute(update_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["updateDocument"]["success"] is True, "Mutation should succeed"
        self.document.refresh_from_db()
        assert self.document.name == "Updated Document", "Description should be updated"
        assert self.document.file == "Updated file", "Priority should be updated"

    def test_delete_document(self):
        delete_query = f"""
            mutation {{
                deleteDocument(id: "{self.document.id}") {{
                    success
                }}
            }}
        """
        response = self.client.execute(delete_query, context_value={"user": self.user})
        print(response)
        if "errors" in response:
            print("Errors:", response["errors"])
        assert response["data"]["deleteDocument"]["success"] is True, "Mutation should succeed"
        with self.assertRaises(Document.DoesNotExist):
            Document.objects.get(pk=self.document.id)
