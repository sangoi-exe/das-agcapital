import graphene
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction

from .models import Event
from apps.activities.models import Activity
from apps.tasks.models import Task


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        interfaces = (graphene.relay.Node,)
        fields = "__all__"  # sem campos sensíveis, utilizar todos
        filter_fields = []


class CreateEvent(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        start_time = graphene.DateTime(required=True)
        end_time = graphene.DateTime(required=True)
        description = graphene.String()
        activity_id = graphene.ID()
        task_id = graphene.ID()

    event = graphene.Field(EventType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, title, start_time, end_time, description=None, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return CreateEvent(event=None, success=False, errors="Authentication required.")

        # validar se apenas um elemento foi associado
        linked_items = sum(1 for key in ["activity_id", "task_id"] if kwargs.get(key))
        if linked_items != 1:
            return CreateEvent(event=None, success=False, errors="An event must be associated with exactly one entity.")

        try:  # criar event com tratamento de validação e erros
            # verificar se o cleiton tem nível de acesso para modificar o evento, ou se é um SU/staff
            cleiton = Cleiton.objects.get(pk=cleiton_id)
            event = Event(title=title, start_time=start_time, end_time=end_time, description=description, cleiton=cleiton)

            project = None
            if "activity_id" in kwargs:
                activity = Activity.objects.get(pk=kwargs["activity_id"])
                project = activity.project
                event.activity = activity
            elif "task_id" in kwargs:
                task = Task.objects.get(pk=kwargs["task_id"])
                project = task.project
                event.task = task

            if project and project.cleiton != cleiton:
                return CreateEvent(event=None, success=False, errors="Permission denied. Not the project owner.")

            with transaction.atomic():
                event.full_clean()
                event.save()
            return CreateEvent(event=event, success=True)
        except ObjectDoesNotExist:
            return CreateEvent(event=None, success=False, errors="Cleiton, activity, or task not found.")
        except ValidationError as e:
            return CreateEvent(event=None, success=False, errors=str(e))


class UpdateEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        start_time = graphene.DateTime()
        end_time = graphene.DateTime()
        description = graphene.String()
        activity_id = graphene.ID()
        task_id = graphene.ID()

    event = graphene.Field(EventType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateEvent(event=None, success=False, errors="Authentication required.")

        linked_items = sum(1 for key in ["activity_id", "task_id"] if kwargs.get(key))
        if linked_items > 1:
            return UpdateEvent(event=None, success=False, errors="An event must be associated with exactly one entity.")

        try:  # update event com tratamento de validação e erros
            event = Event.objects.get(pk=id)
            # verificar se o cleiton tem nível de acesso para modificar o evento, ou se é um SU/staff
            if event.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return UpdateEvent(event=None, success=False, errors="Permission denied. Not the event owner.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                for key, value in kwargs.items():
                    if value and key in ["activity_id", "task_id"]:  # lidar com o elemento associado, task ou activity
                        model_class = Activity if key == "activity_id" else Task
                        entity = model_class.objects.get(pk=value)
                        setattr(event, key[:-3], entity)
                    elif value:  # modificar os outros dados
                        setattr(event, key, value)
                event.full_clean()  # validar antes de salvar
                event.save()
                return UpdateEvent(event=event, success=True)
        except ObjectDoesNotExist:
            return UpdateEvent(event=None, success=False, errors="Event or associated entity not found.")
        except ValidationError as e:
            return UpdateEvent(event=None, success=False, errors=str(e))


class DeleteEvent(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteEvent(success=False, errors="Authentication required.")

        try:  # delete event com tratamento de validação e erros
            event = Event.objects.get(pk=id)
            if event.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return DeleteEvent(success=False, errors="Permission denied. Not the event owner.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                event.delete()
            return DeleteEvent(success=True)
        except ObjectDoesNotExist:
            return DeleteEvent(success=False, errors="Event not found.")


class Mutation(graphene.ObjectType):
    create_event = CreateEvent.Field()
