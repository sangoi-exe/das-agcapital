import graphene
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Cleiton


class CleitonType(DjangoObjectType):
    class Meta:
        model = Cleiton
        interfaces = (graphene.relay.Node,)
        filter_fields = ["name", "email", "phone", "address"]
        fields = "__all__"


class CreateCleiton(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        address = graphene.String()

    cleiton = graphene.Field(CleitonType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        if not (user.is_superuser or user.is_staff):  # verificando nível de acesso
            return CreateCleiton(cleiton=None, success=False, errors="Permission denied.")

        try:  # criar cleiton com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                cleiton = Cleiton(**kwargs)
                cleiton.full_clean()  # validar antes de salvar
                cleiton.save()
            return CreateCleiton(cleiton=cleiton, success=True)
        except ValidationError as e:
            return CreateCleiton(cleiton=None, success=False, errors=str(e))


class UpdateCleiton(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        address = graphene.String()

    cleiton = graphene.Field(CleitonType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        try:  # update de cleiton com tratamento de validação e erros
            cleiton = Cleiton.objects.get(pk=id)
            # verificando nível de acesso
            if not (user.is_superuser or user.is_staff or (cleiton.user and cleiton.user == user)):
                return UpdateCleiton(cleiton=None, success=False, errors="Permission denied.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                for key, value in kwargs.items():
                    setattr(cleiton, key, value)
                cleiton.full_clean()  # validar antes de salvar
                cleiton.save()
            return UpdateCleiton(cleiton=cleiton, success=True)
        except ObjectDoesNotExist:
            return UpdateCleiton(cleiton=None, success=False, errors="Cleiton not found.")
        except ValidationError as e:
            return UpdateCleiton(cleiton=None, success=False, errors=str(e))


class DeleteCleiton(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        if not (user.is_superuser or user.is_staff):
            return DeleteCleiton(success=False, errors="Permission denied.")

        try:  # deletar cleiton com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                cleiton = Cleiton.objects.get(pk=id)
                cleiton.delete()
            return DeleteCleiton(success=True)
        except ObjectDoesNotExist:
            return DeleteCleiton(success=False, errors="Cleiton not found.")


class Mutation(graphene.ObjectType):
    create_cleiton = CreateCleiton.Field()
    update_cleiton = UpdateCleiton.Field()
    delete_cleiton = DeleteCleiton.Field()
