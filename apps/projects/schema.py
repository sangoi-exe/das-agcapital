import graphene
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Project
from apps.accounts.models import DefaultAccount


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        interfaces = (graphene.relay.Node,)
        filter_fields = ["owner", "name", "description", "status", "start_date", "estimated_end_date"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateProject(graphene.Mutation):
    class Arguments:
        owner = graphene.String(required=True)
        name = graphene.String(required=True)
        description = graphene.String()
        status = graphene.String()
        start_date = graphene.Date()
        estimated_end_date = graphene.Date()

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.get("user") if isinstance(info.context, dict) else info.context.user

        if user.is_anonymous:
            return CreateProject(project=None, success=False, errors="Authentication required.")

        try:  # criar project com tratamento de validação e erros
            owner = DefaultAccount.objects.get(username=kwargs.pop("owner").lower())
            owner_id = owner.id

            if not (user.is_superuser or user.is_staff):
                return CreateProject(project=None, success=False, errors="Permission denied.")

            with transaction.atomic():
                project = Project(owner_id=owner_id, **kwargs)
                project.full_clean()  # validar antes de salvar
                project.save()
            return CreateProject(project=project, success=True)

        except DefaultAccount.DoesNotExist:
            return CreateProject(project=None, success=False, errors="Account not found.")

        except ValidationError as e:
            return CreateProject(project=None, success=False, errors=f"Validation Error: {e}")


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        owner = graphene.String()
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

        if user.is_anonymous:
            return UpdateProject(project=None, success=False, errors="Authentication required.")

        try:  # update de project com tratamento de validação e erros
            project = Project.objects.get(pk=id)

            if not (user.id == project.owner or user.is_superuser or user.is_staff):
                return UpdateProject(project=None, success=False, errors="Permission denied.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                if "owner" in kwargs:
                    new_owner = kwargs.pop("owner").lower()
                    if new_owner != project.owner:
                        new_owner = DefaultAccount.objects.get(username=new_owner)
                        project.owner = new_owner
                for key, value in kwargs.items():
                    setattr(project, key, value)  # atualizar apenas os campos fornecidos
                project.full_clean()  # validar mudanças antes de salvar
                project.save()
            return UpdateProject(project=project, success=True)

        except DefaultAccount.DoesNotExist:
            return UpdateProject(project=None, success=False, errors="Owner not found.")

        except Project.DoesNotExist:
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

        if user.is_anonymous:
            return DeleteProject(success=False, errors="Authentication required.")

        try:  # deletar project com tratamento de validação e erros
            project = Project.objects.get(pk=id)

            if not (user.id == project.owner or user.is_superuser or user.is_staff):
                return UpdateProject(project=None, success=False, errors="Permission denied.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                project.delete()
            return DeleteProject(success=True)
        
        except ObjectDoesNotExist:
            return DeleteProject(success=False, errors="Project not found.")


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
