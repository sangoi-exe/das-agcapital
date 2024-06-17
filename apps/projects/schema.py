import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Project
from apps.cleitons.models import Cleiton


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        interfaces = (graphene.relay.Node,)
        filter_fields = ["name", "description", "cleiton_id", "status", "start_date", "estimated_end_date"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        cleiton_id = graphene.ID(required=True)
        status = graphene.String()
        start_date = graphene.Date()
        estimated_end_date = graphene.Date()

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        if not user.is_authenticated:
            return CreateProject(project=None, success=False, errors="Authentication required.")

        try:  # criar project com tratamento de validação e erros
            cleiton_id = kwargs.pop("cleiton_id")
            cleiton = Cleiton.objects.get(pk=cleiton_id)
            if not (user.is_superuser or user.is_staff):
                return CreateProject(project=None, success=False, errors="Permission denied.")

            with transaction.atomic():
                project = Project(cleiton=cleiton, **kwargs)
                project.full_clean()  # validar antes de salvar
                project.save()
            return CreateProject(project=project, success=True)
        except ObjectDoesNotExist:
            return CreateProject(project=None, success=False, errors="Cleiton not found.")
        except ValidationError as e:
            return CreateProject(project=None, success=False, errors=str(e))


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        status = graphene.String()
        start_date = graphene.Date()
        estimated_end_date = graphene.Date()

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        if not user.is_authenticated:
            return UpdateProject(project=None, success=False, errors="Authentication required.")

        try:  # update de project com tratamento de validação e erros
            project = Project.objects.get(pk=id)
            if project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return UpdateProject(project=None, success=False, errors="Permission denied.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                for key, value in kwargs.items():
                    setattr(project, key, value)  # atualizar apenas os campos fornecidos
                project.full_clean()  # validar mudanças antes de salvar
                project.save()
            return UpdateProject(project=project, success=True)
        except ObjectDoesNotExist:
            return UpdateProject(project=None, success=False, errors="Project not found.")
        except ValidationError as e:
            return UpdateProject(project=None, success=False, errors=str(e))


class DeleteProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user
        if not user.is_authenticated:
            return DeleteProject(success=False, errors="Authentication required.")

        try:  # deletar project com tratamento de validação e erros
            project = Project.objects.get(pk=id)
            if project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return DeleteProject(success=False, errors="Permission denied.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                project.delete()
            return DeleteProject(success=True)
        except ObjectDoesNotExist:
            return DeleteProject(success=False, errors="Project not found.")


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
