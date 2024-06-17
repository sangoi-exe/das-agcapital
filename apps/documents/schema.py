import graphene
import django_filters
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Document


class DocumentType(DjangoObjectType):
    class Meta:
        model = Document
        interfaces = (graphene.relay.Node,)
        filter_fields = ["name", "uploaded_at", "project"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateDocument(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        uploaded_at = graphene.String()
        project = graphene.String()

    document = graphene.Field(DocumentType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        try:  # criar documento com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                document = Document(**kwargs)
                document.full_clean()  # validar antes de salvar
                document.save()
            return CreateDocument(document=document, success=True)
        except ValidationError as e:
            return CreateDocument(document=None, success=False, errors=str(e))


class UpdateDocument(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        uploaded_at = graphene.String()
        project = graphene.String()

    document = graphene.Field(DocumentType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:  # update de documento com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                document = Document.objects.get(pk=id)
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
        try:  # deletar documento com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                document = Document.objects.get(pk=id)
                document.delete()
            return DeleteDocument(success=True)
        except ObjectDoesNotExist:
            return DeleteDocument(success=False, errors="Document not found.")


class Mutation(graphene.ObjectType):
    create_document = CreateDocument.Field()
    update_document = UpdateDocument.Field()
    delete_document = DeleteDocument.Field()
