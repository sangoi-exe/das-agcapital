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
        file = graphene.String(required=True)  # simular upload de file para fins de testes
        project_id = graphene.ID(required=True)

    document = graphene.Field(DocumentType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return CreateDocument(document=None, success=False, errors="Authentication required.")

        try:  # criar documento com tratamento de validação e erros
            project_id = kwargs.get("project_id")
            project = Project.objects.get(pk=project_id)
            if project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return CreateDocument(document=None, success=False, errors="Permission denied.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                document = Document(**kwargs)
                document.project = project  # associar documento ao seu respectivo projeto
                document.full_clean()
                document.save()
            return CreateDocument(document=document, success=True)
        except ObjectDoesNotExist:
            return CreateDocument(document=None, success=False, errors="Project not found.")
        except ValidationError as e:
            return CreateDocument(document=None, success=False, errors=str(e))


class UpdateDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        file = graphene.String()  # simular upload de file para fins de testes

    document = graphene.Field(DocumentType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        user = info.context.user
        try:  # update de documento com tratamento de validação e erros
            document = Document.objects.get(pk=id)
            if document.project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return UpdateDocument(document=None, success=False, errors="Permission denied.")

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

    success = graphene.Boolean()

    def mutate(self, info, id):
        user = info.context.user
        try:  # deletar documento com tratamento de validação e erros
            document = Document.objects.get(pk=id)
            if document.project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return DeleteDocument(success=False, errors="Permission denied.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                document.delete()
            return DeleteDocument(success=True)
        except ObjectDoesNotExist:
            return DeleteDocument(success=False, errors="Document not found.")


class Mutation(graphene.ObjectType):
    create_document = CreateDocument.Field()
    update_document = UpdateDocument.Field()
    delete_document = DeleteDocument.Field()
