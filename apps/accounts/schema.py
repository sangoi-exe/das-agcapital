import graphene
from graphene_django.types import DjangoObjectType
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from .models import DefaultAccount


class UserType(DjangoObjectType):
    class Meta:
        model = DefaultAccount
        interfaces = (graphene.relay.Node,)
        fields = ["id", "username", "email", "is_staff"]
        filter_fields = ["id", "username", "email", "is_staff"]


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        is_staff = graphene.Boolean(required=False)

    default_account_user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            print("User is anonymous.")
            return CreateUser(default_account_user=None, success=False, errors="Authentication required.")

        if not (user.is_superuser or user.is_staff):
            print("User does not have the necessary access level.")
            return CreateUser(default_account_user=None, success=False, errors="Access denied.")

        try:  # criar account com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                if "password" in kwargs:
                    kwargs["password"] = make_password(kwargs["password"])  # tratar senha de modo seguro

                if not user.is_superuser and kwargs.get("is_staff", False):
                    kwargs["is_staff"] = False

                default_account_user = DefaultAccount(**kwargs)
                default_account_user.full_clean()  # validar antes de salvar
                default_account_user.save()
                print("User created successfully.")
            return CreateUser(default_account_user=default_account_user, success=True)

        except ValidationError as e:
            return CreateUser(default_account_user=None, success=False, errors=str(e))

        except Exception as e:
            return CreateUser(default_account_user=None, success=False, errors="An unexpected error occurred.")


class CreateStaff(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        is_staff = graphene.Boolean(required=False)

    default_account_user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, is_staff=False, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            print("User is anonymous")
            return CreateStaff(default_account_user=None, success=False, errors="Authentication required.")

        # Staff pode criar apenas usuários comuns, superuser pode criar qualquer tipo
        if not (user.is_superuser or (user.is_staff and not is_staff)):
            return CreateStaff(default_account_user=None, success=False, errors="Access denied.")

        try:  # criar account com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                if "password" in kwargs:
                    kwargs["password"] = make_password(kwargs["password"])  # tratar senha de modo seguro

                default_account_user = DefaultAccount(**kwargs)
                default_account_user.full_clean()  # validar antes de salvar
                default_account_user.save()
                print("User created successfully.")
            return CreateStaff(default_account_user=default_account_user, success=True)

        except ValidationError as e:
            return CreateStaff(default_account_user=None, success=False, errors=str(e))

        except Exception as e:
            return CreateStaff(default_account_user=None, success=False, errors="An unexpected error occurred.")


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()  # habilitar mudança de senha
        is_staff = graphene.Boolean()  # habilitar mudança de nível

    default_account_user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            print("User is anonymous.")
            return UpdateUser(default_account_user=None, success=False, errors="Authentication required.")

        default_account_user = DefaultAccount.objects.get(pk=id)

        # verificar nível de acesso para mudar nível do usuário
        if "is_staff" in kwargs:
            if user.is_superuser:
                default_account_user.is_staff = kwargs.pop("is_staff")

            elif user == default_account_user or user.is_staff:
                return UpdateUser(default_account_user=None, success=False, errors="Access denied.")

        try:
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco

                for field, value in kwargs.items():
                    if hasattr(default_account_user, field):
                        if field == "password":  # tratamento especial para a senha
                            default_account_user.set_password(value)
                        else:
                            setattr(default_account_user, field, value)
                default_account_user.full_clean()  # validar antes de salvar
                default_account_user.save()
                return UpdateUser(default_account_user=default_account_user, success=True)

        except ValidationError as e:
            return UpdateUser(default_account_user=None, success=False, errors=str(e))

        except ObjectDoesNotExist:
            return UpdateUser(default_account_user=None, success=False, errors="Account not found.")

        except Exception as e:
            return UpdateUser(default_account_user=None, success=False, errors="An unexpected error occurred.")


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            print("User is anonymous.")
            return DeleteUser(success=False, errors="Authentication required")

        try:
            default_account_user = DefaultAccount.objects.get(pk=id)

            # verificar nível de acesso para deletar staff
            if default_account_user.is_staff:
                if not user.is_superuser:
                    print("Insufficient permissions to delete a staff account.")
                    return DeleteUser(success=False, errors="Insufficient permissions to delete a staff account.")
            # verificar nível de acesso para deletar usuário comum
            if not (user.is_superuser or user.is_staff):
                print("Insufficient access level.")
                return DeleteUser(success=False, errors="Permission denied.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                default_account_user.delete()
            return DeleteUser(success=True, errors=None)

        except ValidationError as e:
            return DeleteUser(default_account_user=None, success=False, errors=str(e))

        except ObjectDoesNotExist:
            return DeleteUser(default_account_user=None, success=False, errors="Account not found.")

        except Exception as e:
            return DeleteUser(default_account_user=None, success=False, errors="An unexpected error occurred.")


class Mutation(graphene.ObjectType):
    create_staff = CreateStaff.Field()
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
