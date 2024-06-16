import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Task


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        interfaces = (graphene.relay.Node,)
        filter_fields = [
            "title",
            "description",
            "due_date",
            "completed",
            "project",
            "activity",
        ]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        description = graphene.String()
        due_date = graphene.String()
        completed = graphene.String()
        project = graphene.String()
        activity = graphene.String()

    task = graphene.Field(TaskType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        try:  # criar task com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                task = Task(**kwargs)
                task.full_clean()  # validar antes de salvar
                task.save()
            return CreateTask(task=task, success=True)
        except ValidationError as e:
            return CreateTask(task=None, success=False, errors=str(e))


class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        file = graphene.String()
        uploaded_at = graphene.String()
        task = graphene.String()

    task = graphene.Field(TaskType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:  # update de task com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                task = Task.objects.get(pk=id)
                for key, value in kwargs.items():
                    setattr(task, key, value)  # atualizar apenas os campos fornecidos
                task.full_clean()  # validar mudanças antes de salvar
                task.save()
            return UpdateTask(task=task, success=True)
        except ObjectDoesNotExist:
            return UpdateTask(task=None, success=False, errors="Task not found.")
        except ValidationError as e:
            return UpdateTask(task=None, success=False, errors=str(e))


class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:  # deletar task com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                task = Task.objects.get(pk=id)
                task.delete()
            return DeleteTask(success=True)
        except ObjectDoesNotExist:
            return DeleteTask(success=False, errors="Task not found.")


class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()
