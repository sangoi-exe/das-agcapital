import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Project


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        interfaces = (graphene.relay.Node,)
        filter_fields = [
            "name",
            "description",
            "cleiton",
            "status",
            "start_date",
            "estimated_end_date",
        ]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateProject(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String()
        cleiton = graphene.String()
        status = graphene.String()
        start_date = graphene.String()
        estimated_end_date = graphene.String()

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        try:  # criar project com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                project = Project(**kwargs)
                project.full_clean()  # validar antes de salvar
                project.save()
            return CreateProject(project=project, success=True)
        except ValidationError as e:
            return CreateProject(project=None, success=False, errors=str(e))


class UpdateProject(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        file = graphene.String()
        uploaded_at = graphene.String()
        project = graphene.String()

    project = graphene.Field(ProjectType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:  # update de project com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                project = Project.objects.get(pk=id)
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

    def mutate(self, info, id):
        try:  # deletar project com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                project = Project.objects.get(pk=id)
                project.delete()
            return DeleteProject(success=True)
        except ObjectDoesNotExist:
            return DeleteProject(success=False, errors="project not found.")


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()
