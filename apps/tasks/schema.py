import graphene
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Task
from apps.projects.models import Project
from apps.activities.models import Activity


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        interfaces = (graphene.relay.Node,)
        filter_fields = ["title", "description", "due_date", "completed", "project_id", "activity_id"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        due_date = graphene.DateTime(required=True)
        completed = graphene.Boolean(required=True)
        project_id = graphene.ID(required=True)
        activity_id = graphene.ID()

    task = graphene.Field(TaskType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return CreateTask(task=None, success=False, errors="Authentication required.")

        try:  # criar task com tratamento de validação e erros
            project = Project.objects.get(pk=kwargs.pop("project_id"))
            if project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return CreateTask(task=None, success=False, errors="Permission denied. Not the project owner.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                task = Task(project=project, **kwargs)
                if "activity_id" in kwargs:
                    task.activity = Activity.objects.get(pk=kwargs.pop("activity_id"))
                task.full_clean()  # validar antes de salvar
                task.save()
            return CreateTask(task=task, success=True)
        except ObjectDoesNotExist:
            return CreateTask(task=None, success=False, errors="Project or activity not found.")
        except ValidationError as e:
            return CreateTask(task=None, success=False, errors=str(e))


class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        due_date = graphene.DateTime()
        completed = graphene.Boolean()
        project_id = graphene.ID()

    task = graphene.Field(TaskType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateTask(task=None, success=False, errors="Authentication required.")

        try:  # update de task com tratamento de validação e erros
            task = Task.objects.get(pk=id)
            project = Project.objects.get(pk=kwargs.pop("project_id", task.project_id))
            if project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return UpdateTask(task=None, success=False, errors="Permission denied. Not the project owner.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                for key, value in kwargs.items():
                    setattr(task, key, value)  # atualizar apenas os campos fornecidos
                task.project = project  # se necessário, ajustar qual o projeto referente a atividade
                task.full_clean()  # validar mudanças antes de salvar
                task.save()
            return UpdateTask(task=task, success=True)
        except ObjectDoesNotExist:
            return UpdateTask(task=None, success=False, errors="Task or project not found.")
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
