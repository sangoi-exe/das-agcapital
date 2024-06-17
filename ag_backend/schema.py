import graphene
from graphene_django.filter import DjangoFilterConnectionField

from apps.accounts.models import Account
from apps.accounts.schema import AccountsType, CreateAccounts, DeleteAccounts, UpdateAccounts
from apps.activities.models import Activity
from apps.activities.schema import ActivityType, CreateActivity, DeleteActivity, UpdateActivity
from apps.cleitons.models import Cleiton
from apps.cleitons.schema import CleitonType, CreateCleiton, DeleteCleiton, UpdateCleiton
from apps.documents.models import Document
from apps.documents.schema import CreateDocument, DeleteDocument, DocumentType, UpdateDocument
from apps.notifications.models import Notification
from apps.notifications.schema import CreateNotification, DeleteNotification, NotificationType, UpdateNotification
from apps.projects.models import Project
from apps.projects.schema import CreateProject, DeleteProject, ProjectType, UpdateProject
from apps.reports.models import Report
from apps.reports.schema import CreateReport, DeleteReport, ReportType, UpdateReport
from apps.tasks.models import Task
from apps.tasks.schema import CreateTask, DeleteTask, TaskType, UpdateTask


class Query(graphene.ObjectType):
    user = graphene.Field(AccountsType, id=graphene.ID(required=True))
    client = graphene.Field(CleitonType, id=graphene.ID(required=True))
    activity = graphene.Field(ActivityType, id=graphene.ID(required=True))
    document = graphene.Field(DocumentType, id=graphene.ID(required=True))
    notification = graphene.Field(NotificationType, id=graphene.ID(required=True))
    project = graphene.Field(ProjectType, id=graphene.ID(required=True))
    report = graphene.Field(ReportType, id=graphene.ID(required=True))
    task = graphene.Field(TaskType, id=graphene.ID(required=True))

    all_clients = DjangoFilterConnectionField(CleitonType)
    all_users = DjangoFilterConnectionField(AccountsType)
    all_activities = DjangoFilterConnectionField(ActivityType)
    all_documents = DjangoFilterConnectionField(DocumentType)
    all_notifications = DjangoFilterConnectionField(NotificationType)
    all_projects = DjangoFilterConnectionField(ProjectType)
    all_reports = DjangoFilterConnectionField(ReportType)
    all_tasks = DjangoFilterConnectionField(TaskType)

    def resolve_user(self, info, id):
        return Account.objects.get(pk=id)

    def resolve_client(self, info, id):
        return Cleiton.objects.get(pk=id)

    def resolve_activity(self, info, id):
        return Activity.objects.get(pk=id)

    def resolve_document(self, info, id):
        return Document.objects.get(pk=id)

    def resolve_notification(self, info, id):
        return Notification.objects.get(pk=id)

    def resolve_project(self, info, id):
        return Project.objects.get(pk=id)

    def resolve_report(self, info, id):
        return Report.objects.get(pk=id)

    def resolve_task(self, info, id):
        return Task.objects.get(pk=id)


class Mutation(graphene.ObjectType):
    create_accounts_user = CreateAccounts.Field()
    update_accounts_user = UpdateAccounts.Field()
    delete_accounts_user = DeleteAccounts.Field()

    create_activity = CreateActivity.Field()
    update_activity = UpdateActivity.Field()
    delete_activity = DeleteActivity.Field()

    create_cleiton = CreateCleiton.Field()
    update_cleiton = UpdateCleiton.Field()
    delete_cleiton = DeleteCleiton.Field()

    create_document = CreateDocument.Field()
    update_document = UpdateDocument.Field()
    delete_document = DeleteDocument.Field()

    create_notification = CreateNotification.Field()
    update_notification = UpdateNotification.Field()
    delete_notification = DeleteNotification.Field()

    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    delete_project = DeleteProject.Field()

    create_report = CreateReport.Field()
    update_report = UpdateReport.Field()
    delete_report = DeleteReport.Field()

    create_task = CreateTask.Field()
    update_task = UpdateTask.Field()
    delete_task = DeleteTask.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
