import graphene
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Document
from apps.projects.models import Project


class DocumentType(DjangoObjectType):
    class Meta:
        model = Document
        interfaces = (graphene.relay.Node,)
        filter_fields = ["name", "uploaded_at", "project_id"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateDocument(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        project_id = graphene.ID(required=True)
        file = graphene.String(required=True)  # simular upload de file para fins de testes
        uploaded_at = graphene.Date(required=True)

    document = graphene.Field(DocumentType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, project_id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        project = Project.objects.get(pk=project_id)

        if not (user.is_superuser or user.is_staff or project.cleiton.username == user.username):
            print("Permission denied.")
            return CreateDocument(document=None, success=False, errors="Permission denied.")

        try:  # criar documento com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                print("Creating document with:", kwargs)
                document = Document(project=project, **kwargs)
                document.full_clean()  # validar antes de salvar
                document.save()
            return CreateDocument(document=document, success=True)
        except ValidationError as e:
            print(f"ObjectDoesNotExist: {str(e)}")
            return CreateDocument(document=None, success=False, errors=str(e))
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return CreateDocument(document=None, success=False, errors="An unexpected error occurred")


class UpdateDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        file = graphene.String()  # simular upload de file para fins de testes

    document = graphene.Field(DocumentType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        document = Document.objects.get(pk=id)

        if not (user.is_superuser or user.is_staff or document.project.cleiton.username == user.username):
            return UpdateDocument(document=None, success=False, errors="Permission denied.")

        try:  # update de documento com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                for key, value in kwargs.items():
                    setattr(document, key, value)  # atualizar apenas os campos fornecidos
                document.full_clean()  # validar mudanças antes de salvar
                document.save()
            return UpdateDocument(document=document, success=True)
        except ObjectDoesNotExist:
            return UpdateDocument(document=None, success=False, errors="Document not found.")
        except ValidationError as e:
            return UpdateDocument(document=None, success=False, errors=str(e))


class DeleteDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    document = graphene.Field(DocumentType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        document = Document.objects.get(pk=id)

        if not (user.is_superuser or user.is_staff or document.project.cleiton.username == user.username):
            return UpdateDocument(document=None, success=False, errors="Permission denied.")

        try:  # deletar documento com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                document.delete()
            return DeleteDocument(success=True)
        except ObjectDoesNotExist:
            return DeleteDocument(success=False, errors="Document not found.")


class Mutation(graphene.ObjectType):
    create_document = CreateDocument.Field()
    update_document = UpdateDocument.Field()
    delete_document = DeleteDocument.Field()
