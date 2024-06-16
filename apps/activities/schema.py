import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Activity


class ActivityType(DjangoObjectType):
    class Meta:
        model = Activity
        interfaces = (graphene.relay.Node,)
        filter_fields = [
            "description",
            "project",
            "priority",
            "status",
            "creation_date",
            "expected_completion_date",
        ]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateActivity(graphene.Mutation):
    class Arguments:
        description = graphene.String(required=True)
        project = graphene.String(required=True)
        priority = graphene.String(required=True)
        status = graphene.String(required=True)
        creation_date = graphene.String(required=True)
        expected_completion_date = graphene.String(required=True)

    activity = graphene.Field(ActivityType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        try:  # criar atividade com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                activity = Activity(**kwargs)
                activity.full_clean()  # validar antes de salvar
                activity.save()
            return CreateActivity(activity=activity, success=True)
        except ValidationError as e:
            return CreateActivity(activity=None, success=False, errors=str(e))


class UpdateActivity(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        description = graphene.String()
        project = graphene.String()
        priority = graphene.String()
        status = graphene.String()
        creation_date = graphene.String()
        expected_completion_date = graphene.String()

    activity = graphene.Field(ActivityType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:  # update de atividade com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                activity = Activity.objects.get(pk=id)
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

    def mutate(self, info, id):
        try:  # deletar atividade com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                activity = Activity.objects.get(pk=id)
                activity.delete()
            return DeleteActivity(success=True)
        except ObjectDoesNotExist:
            return DeleteActivity(success=False, errors="Activity not found.")


class Mutation(graphene.ObjectType):
    create_activity = CreateActivity.Field()
    update_activity = UpdateActivity.Field()
    delete_activity = DeleteActivity.Field()
