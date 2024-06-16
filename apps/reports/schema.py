import graphene
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from graphene_django.types import DjangoObjectType

from .models import Report


class ReportType(DjangoObjectType):
    class Meta:
        model = Report
        interfaces = (graphene.relay.Node,)
        filter_fields = ["title", "content", "generated_at", "report"]
        fields = "__all__"  # sem campos sensíveis, utilizar todos


class CreateReport(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String()
        cleiton = graphene.String()
        status = graphene.String()
        start_date = graphene.String()
        estimated_end_date = graphene.String()

    report = graphene.Field(ReportType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        try:  # criar report com tratamento de validação e erros
            with transaction.atomic():  # transação atômica para garantir a integridade da manipulação no banco
                report = Report(**kwargs)
                report.full_clean()  # validar antes de salvar
                report.save()
            return CreateReport(report=report, success=True)
        except ValidationError as e:
            return CreateReport(report=None, success=False, errors=str(e))


class UpdateReport(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        file = graphene.String()
        uploaded_at = graphene.String()
        report = graphene.String()

    report = graphene.Field(ReportType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:  # update de report com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                report = Report.objects.get(pk=id)
                for key, value in kwargs.items():
                    setattr(report, key, value)  # atualizar apenas os campos fornecidos
                report.full_clean()  # validar mudanças antes de salvar
                report.save()
            return UpdateReport(report=report, success=True)
        except ObjectDoesNotExist:
            return UpdateReport(report=None, success=False, errors="Report not found.")
        except ValidationError as e:
            return UpdateReport(report=None, success=False, errors=str(e))


class DeleteReport(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:  # deletar report com tratamento de validação e erros
            with transaction.atomic():  # utilizar transação atômica para garantir a integridade da manipulação no banco
                report = Report.objects.get(pk=id)
                report.delete()
            return DeleteReport(success=True)
        except ObjectDoesNotExist:
            return DeleteReport(success=False, errors="report not found.")


class Mutation(graphene.ObjectType):
    create_report = CreateReport.Field()
    update_report = UpdateReport.Field()
    delete_report = DeleteReport.Field()
