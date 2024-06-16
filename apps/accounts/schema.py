import graphene
from .models import Account
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class AccountsType(DjangoObjectType):
    class Meta:
        model = Account
        interfaces = (graphene.relay.Node,)
        filter_fields = ["id", "username", "email", "cpf", "phone_number"]
        fields = ("id", "username", "email", "cpf", "phone_number")


class CreateAccounts(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        cpf = graphene.String(required=True)
        phone_number = graphene.String(required=True)

    accounts_user = graphene.Field(AccountsType)
    success = graphene.Boolean()

    def mutate(self, info, username, email, cpf, phone_number):
        try:
            with transaction.atomic():
                accounts_user = Account(username=username, email=email, cpf=cpf, phone_number=phone_number)
                accounts_user.full_clean()
                accounts_user.save()
            return CreateAccounts(accounts_user=accounts_user, success=True)
        except ValidationError as e:
            return CreateAccounts(accounts_user=None, success=False, errors=str(e))


class UpdateAccounts(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        cpf = graphene.String()
        phone_number = graphene.String()

    accounts_user = graphene.Field(AccountsType)
    success = graphene.Boolean()

    def mutate(self, info, id, username=None, email=None, cpf=None, phone_number=None):
        try:
            with transaction.atomic():
                accounts_user = Account.objects.get(pk=id)
                if username:
                    accounts_user.username = username
                if email:
                    accounts_user.email = email
                if cpf:
                    accounts_user.cpf = cpf
                if phone_number:
                    accounts_user.phone_number = phone_number
                accounts_user.full_clean()
                accounts_user.save()
            return UpdateAccounts(accounts_user=accounts_user, success=True)
        except ObjectDoesNotExist:
            return UpdateAccounts(accounts_user=None, success=False, errors="Accounts not found.")
        except ValidationError as e:
            return UpdateAccounts(accounts_user=None, success=False, errors=str(e))


class DeleteAccounts(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            with transaction.atomic():
                accounts_user = Account.objects.get(pk=id)
                accounts_user.delete()
            return DeleteAccounts(success=True)
        except ObjectDoesNotExist:
            return DeleteAccounts(success=False, errors="Accounts not found.")


class Mutation(graphene.ObjectType):
    create_accounts_user = CreateAccounts.Field()
    update_accounts_user = UpdateAccounts.Field()
    delete_accounts_user = DeleteAccounts.Field()
