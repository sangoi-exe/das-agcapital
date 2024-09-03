import graphene
from .models import Activity
from apps.projects.models import Project
from apps.accounts.models import DefaultAccount

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from graphene_django.types import DjangoObjectType


class ActivityType(DjangoObjectType):
    project_id = graphene.ID()

    class Meta:
        model = Activity
        interfaces = (graphene.relay.Node,)
        filter_fields = ["project_id", "name", "priority", "status", "creation_date", "expected_completion_date"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateActivity(graphene.Mutation):
    class Arguments:
        project_id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        priority = graphene.String(required=True)
        status = graphene.String(required=True)
        creation_date = graphene.Date(required=True)
        expected_completion_date = graphene.Date(required=True)

    activity = graphene.Field(ActivityType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, project_id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            return CreateActivity(activity=None, success=False, errors="Authentication required.")

        try:  # criar atividade com tratamento de validação e erros
            project = Project.objects.get(pk=project_id)

            if not (user.is_superuser or user.is_staff or project.owner_id == user.id):
                return CreateActivity(activity=None, success=False, errors="Permission denied.")

            created_by = DefaultAccount.objects.get(username=user)
            created_by_id = created_by.id

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                activity = Activity(project_id=project.id, created_by_id=created_by_id, **kwargs)
                activity.full_clean()  # validar antes de salvar
                activity.save()
            return CreateActivity(activity=activity, success=True)

        except Project.DoesNotExist:
            return CreateActivity(activity=None, success=False, errors="Project not found.")

        except ValidationError as e:
            return CreateActivity(activity=None, success=False, errors=f"Validation Error: {e}")


class UpdateActivity(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        project_id = graphene.ID()
        created_by = graphene.String()
        name = graphene.String()
        description = graphene.String()
        priority = graphene.String()
        status = graphene.String()
        creation_date = graphene.String()
        expected_completion_date = graphene.String()

    activity = graphene.Field(ActivityType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            return UpdateActivity(activity=None, success=False, errors="Authentication required.")

        try:  # update de atividade com tratamento de validação e erros
            activity = Activity.objects.get(pk=id)

            if not (user.is_superuser or user.is_staff or activity.created_by_id == user.id):
                return UpdateActivity(activity=None, success=False, errors="Permission denied.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                if "created_by" in kwargs:
                    new_created_by = kwargs.pop("created_by").lower()
                    if new_created_by != activity.created_by:
                        new_created_by = DefaultAccount.objects.get(username=new_created_by)
                        activity.created_by = new_created_by

                for key, value in kwargs.items():
                    setattr(activity, key, value)  # atualizar apenas os campos fornecidos
                activity.full_clean()  # validar antes de salvar
                activity.save()
            return UpdateActivity(activity=activity, success=True)

        except ObjectDoesNotExist:
            return UpdateActivity(activity=None, success=False, errors="Activity not found.")

        except ValidationError as e:
            return UpdateActivity(activity=None, success=False, errors=str(e))


class DeleteActivity(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            return DeleteActivity(activity=None, success=False, errors="Authentication required.")

        try:  # deletar atividade com tratamento de validação e erros
            activity = Activity.objects.get(pk=id)

            if not (user.is_superuser or user.is_staff or activity.created_by_id == user.id):
                return DeleteActivity(activity=None, success=False, errors="Permission denied.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                activity.delete()
            return DeleteActivity(success=True)

        except ObjectDoesNotExist:
            return DeleteActivity(success=False, errors="Activity not found.")


class Mutation(graphene.ObjectType):
    create_activity = CreateActivity.Field()
    update_activity = UpdateActivity.Field()
    delete_activity = DeleteActivity.Field()
