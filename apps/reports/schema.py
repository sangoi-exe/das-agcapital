import graphene
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from .models import Report
from apps.projects.models import Project


class ReportType(DjangoObjectType):
    class Meta:
        model = Report
        interfaces = (graphene.relay.Node,)
        filter_fields = ["title", "content", "project", "generated_at"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateReport(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        project_id = graphene.ID(required=True)
        generated_at = graphene.DateTime(required=True)

    report = graphene.Field(ReportType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return CreateReport(report=None, success=False, errors="Authentication required.")

        try:  # criar report com tratamento de validação e erros
            project_id = kwargs.pop("project_id")
            project = Project.objects.get(pk=project_id)

            if project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return CreateReport(report=None, success=False, errors="Permission denied. Not the project owner.")

            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                report = Report(project=project, **kwargs)
                report.full_clean()  # validar antes de salvar
                report.save()
            return CreateReport(report=report, success=True)
        except ObjectDoesNotExist:
            return CreateReport(report=None, success=False, errors="Project not found.")
        except ValidationError as e:
            return CreateReport(report=None, success=False, errors=str(e))


class UpdateReport(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        project_id = graphene.ID(required=True)
        generated_at = graphene.DateTime(required=True)

    report = graphene.Field(ReportType)
    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return UpdateReport(report=None, success=False, errors="Authentication required.")

        try:  # update report com tratamento de validação e erros
            report = Report.objects.get(pk=id)
            project = Project.objects.get(pk=kwargs["project_id"])
            cleiton = Cleiton.objects.get(pk=kwargs["cleiton_id"])

            if project.cleiton != cleiton or project.cleiton.user != user:
                return UpdateReport(report=None, success=False, errors="Permission denied. Not the project owner or mismatched author.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                for key, value in kwargs.items():
                    if key in ["title", "content", "generated_at"]:
                        setattr(report, key, value)  # atualizar apenas os campos fornecidos
                report.project = project  # se necessário, ajustar qual o projeto referente ao report
                report.full_clean()  # validar mudanças antes de salvar
                report.save()
            return UpdateReport(report=report, success=True)
        except ObjectDoesNotExist:
            return UpdateReport(report=None, success=False, errors="Report or project not found.")
        except ValidationError as e:
            return UpdateReport(report=None, success=False, errors=str(e))


class DeleteReport(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.String()

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return DeleteReport(success=False, errors="Authentication required.")

        try:  # deletar report com tratamento de validação e erros
            report = Report.objects.get(pk=id)
            if report.project.cleiton.user != user and not (user.is_superuser or user.is_staff):
                return DeleteReport(success=False, errors="Permission denied. Not the project owner.")

            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                report.delete()
            return DeleteReport(success=True)
        except ObjectDoesNotExist:
            return DeleteReport(success=False, errors="Report not found.")


class Mutation(graphene.ObjectType):
    create_report = CreateReport.Field()
    update_report = UpdateReport.Field()
    delete_report = DeleteReport.Field()
