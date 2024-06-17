import graphene
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Account


class AccountsType(DjangoObjectType):
    class Meta:
        model = Account
        interfaces = (graphene.relay.Node,)
        fields = ["id", "username", "email"]
        filter_fields = ["id", "username", "email"]


class CreateAccounts(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    accounts_user = graphene.Field(AccountsType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            print("User is anonymous")
            return CreateAccounts(accounts_user=None, success=False, errors="Authentication required")

        if not user.is_superuser:  # verificar se é su
            print("User is not superuser")
            return CreateAccounts(accounts_user=None, success=False, errors="Permission denied.")

        try:  # criar account com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                if "password" in kwargs:
                    kwargs["password"] = make_password(kwargs["password"])  # tratar senha de modo seguro

                accounts_user = Account(**kwargs)
                accounts_user.full_clean()  # validar antes de salvar
                accounts_user.save()
                print("User created successfully")
            return CreateAccounts(accounts_user=accounts_user, success=True)
        except ValidationError as e:
            print(f"Validation error: {e}")
            return CreateAccounts(accounts_user=None, success=False, errors=str(e))
        except Exception as e:
            return CreateAccounts(accounts_user=None, success=False, errors="An unexpected error occurred")


class UpdateAccounts(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()  # habilitar mudança de senha

    accounts_user = graphene.Field(AccountsType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            return UpdateAccounts(accounts_user=None, success=False, errors="Authentication required")

        try:
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                accounts_user = Account.objects.get(pk=id)
                if accounts_user != user and not user.is_superuser:  # verificar se é o próprio usuário ou su
                    return UpdateAccounts(accounts_user=None, success=False, errors="Permission denied.")

                for field, value in kwargs.items():
                    if hasattr(accounts_user, field):
                        if field == "password":  # tratamento especial para a senha
                            accounts_user.set_password(value)
                        else:
                            setattr(accounts_user, field, value)
                accounts_user.full_clean()  # validar antes de salvar
                accounts_user.save()
                return UpdateAccounts(accounts_user=accounts_user, success=True)
        except ObjectDoesNotExist:
            return UpdateAccounts(accounts_user=None, success=False, errors="Account not found.")
        except ValidationError as e:
            return UpdateAccounts(accounts_user=None, success=False, errors=str(e))


class DeleteAccounts(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        print(f"Context user in mutate: {user}")

        if user.is_anonymous:
            return DeleteAccounts(success=False, errors="Authentication required")

        if not user.is_superuser:  # verificar se é su
            return DeleteAccounts(success=False, errors="Permission denied.")

        try:
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                accounts_user = Account.objects.get(pk=id)
                accounts_user.delete()
            return DeleteAccounts(success=True)
        except ObjectDoesNotExist:
            return DeleteAccounts(success=False, errors="Account not found.")


class Mutation(graphene.ObjectType):
    create_accounts_user = CreateAccounts.Field()
    update_accounts_user = UpdateAccounts.Field()
    delete_accounts_user = DeleteAccounts.Field()
