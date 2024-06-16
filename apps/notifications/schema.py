import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Notification


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        interfaces = (graphene.relay.Node,)
        filter_fields = [
            "recipient",
            "title",
            "message",
            "created_at",
            "read",
            "read_at",
        ]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateNotification(graphene.Mutation):
    class Arguments:
        recipient = graphene.String()
        title = graphene.String()
        message = graphene.String()
        created_at = graphene.String()
        read = graphene.String()
        read_at = graphene.String()

    notification = graphene.Field(NotificationType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        try:  # criar notification com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                notification = Notification(**kwargs)
                notification.full_clean()  # validar antes de salvar
                notification.save()
            return CreateNotification(notification=notification, success=True)
        except ValidationError as e:
            return CreateNotification(notification=None, success=False, errors=str(e))


class UpdateNotification(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        file = graphene.String()
        uploaded_at = graphene.String()
        project = graphene.String()

    notification = graphene.Field(NotificationType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:  # update de notification com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                notification = Notification.objects.get(pk=id)
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
        try:  # deletar notification com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                notification = Notification.objects.get(pk=id)
                notification.delete()
            return DeleteNotification(success=True)
        except ObjectDoesNotExist:
            return DeleteNotification(success=False, errors="Notification not found.")


class Mutation(graphene.ObjectType):
    create_notification = CreateNotification.Field()
    update_notification = UpdateNotification.Field()
    delete_notification = DeleteNotification.Field()
