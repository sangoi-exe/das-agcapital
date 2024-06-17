import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Notification
from apps.activities.models import Activity
from apps.cleitons.models import Cleiton
from apps.documents.models import Document
from apps.projects.models import Project
from apps.reports.models import Report
from apps.tasks.models import Task


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        interfaces = (graphene.relay.Node,)
        fields = "__all__"  # sem campos sensíveis, utilizar todos
        filter_fields = ["cleiton_id", "project_id", "activity_id", "report_id", "task_id", "document_id"]


class CreateNotification(graphene.Mutation):
    class Arguments:
        cleiton_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        message = graphene.String(required=True)
        project_id = graphene.ID()
        activity_id = graphene.ID()
        report_id = graphene.ID()
        task_id = graphene.ID()
        document_id = graphene.ID()

    notification = graphene.Field(NotificationType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, cleiton_id, title, message, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return CreateNotification(notification=None, success=False, errors="Authentication required.")

        # validar se apenas um elemento foi associado
        linked_items = sum(1 for key in ["project_id", "activity_id", "report_id", "task_id", "document_id"] if kwargs.get(key))
        if linked_items != 1:
            return CreateNotification(notification=None, success=False, errors="A notification must be associated with exactly one entity.")

        try:  # criar notification com tratamento de validação e erros
            cleiton = Cleiton.objects.get(pk=cleiton_id)
            # verificar se o cleiton tem nível de acesso para criar a notificação, ou se é um SU/staff
            if cleiton.user != user and not (user.is_superuser or user.is_staff):
                return CreateNotification(notification=None, success=False, errors="Permission denied. Not the author.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                notification = Notification(title=title, message=message, cleiton=cleiton)
                for key, value in kwargs.items():
                    if value:
                        model_class = {
                            "project_id": Project,
                            "activity_id": Activity,
                            "report_id": Report,
                            "task_id": Task,
                            "document_id": Document,
                        }[key[:-3]]
                        entity = model_class.objects.get(pk=value)
                        setattr(notification, key[:-3], entity)
                notification.full_clean()  # validar antes de salvar
                notification.save()
                return CreateNotification(notification=notification, success=True)
        except ObjectDoesNotExist:
            return CreateNotification(notification=None, success=False, errors="Entity or author not found.")
        except ValidationError as e:
            return CreateNotification(notification=None, success=False, errors=str(e))


class UpdateNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        message = graphene.String()

    notification = graphene.Field(NotificationType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateNotification(notification=None, success=False, errors="Authentication required.")

        try:  # update de notification com tratamento de validação e erros
            notification = Notification.objects.get(pk=id)
            # verificar se o cleiton tem nível de acesso para modificar a notificação, ou se é um SU/staff
            if notification.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return UpdateNotification(notification=None, success=False, errors="Permission denied. Not the notification author.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                # Atualizar apenas os campos fornecidos
                for key, value in kwargs.items():
                    setattr(notification, key, value)  # atualizar apenas os campos fornecidos
                notification.full_clean()  # validar mudanças antes de salvar
                notification.save()
                return UpdateNotification(notification=notification, success=True)
        except ObjectDoesNotExist:
            return UpdateNotification(notification=None, success=False, errors="Notification not found.")
        except ValidationError as e:
            return UpdateNotification(notification=None, success=False, errors=str(e))


class DeleteNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            with transaction.atomic():
                notification = Notification.objects.get(pk=id)
                notification.delete()
            return DeleteNotification(success=True)
        except ObjectDoesNotExist:
            return DeleteNotification(success=False, errors="Notification not found.")


class DeleteNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteNotification(success=False, errors="Authentication required.")

        try:  # deletar notification com tratamento de validação e erros
            notification = Notification.objects.get(pk=id)
            # verificar se o cleiton tem nível de acesso para deletar a notificação, ou se é um SU/staff
            if notification.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return DeleteNotification(success=False, errors="Permission denied. Not the notification author.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                notification.delete()
                return DeleteNotification(success=True)
        except ObjectDoesNotExist:
            return DeleteNotification(success=False, errors="Notification not found.")


class Mutation(graphene.ObjectType):
    create_notification = CreateNotification.Field()
    update_notification = UpdateNotification.Field()
    delete_notification = DeleteNotification.Field()
