import graphene
from graphene_django.types import DjangoObjectType
from apps.cleitons.models import Cleiton
from apps.projects.models import Project
from apps.activities.models import Activity
from apps.tasks.models import Task
from apps.documents.models import Document
from apps.reports.models import Report
from apps.notifications.models import Notification

class CleitonType(DjangoObjectType):
    class Meta:
        model = Cleiton

class ProjectType(DjangoObjectType):
    class Meta:
        model = Project

class ActivityType(DjangoObjectType):
    class Meta:
        model = Activity

class TaskType(DjangoObjectType):
    class Meta:
        model = Task

class DocumentType(DjangoObjectType):
    class Meta:
        model = Document

class ReportType(DjangoObjectType):
    class Meta:
        model = Report

class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification

class Query(graphene.ObjectType):
    all_clients = graphene.List(CleitonType)
    all_projects = graphene.List(ProjectType)
    all_activities = graphene.List(ActivityType)
    all_tasks = graphene.List(TaskType)
    all_documents = graphene.List(DocumentType)
    all_reports = graphene.List(ReportType)
    all_notifications = graphene.List(NotificationType)

    def resolve_all_clients(self, info, **kwargs):
        return Cleiton.objects.all()
    
    def resolve_all_projects(self, info, **kwargs):
        return Project.objects.all()

    def resolve_all_activities(self, info, **kwargs):
        return Activity.objects.all()

    def resolve_all_tasks(self, info, **kwargs):
        return Task.objects.all()

    def resolve_all_documents(self, info, **kwargs):
        return Document.objects.all()

    def resolve_all_reports(self, info, **kwargs):
        return Report.objects.all()

    def resolve_all_notifications(self, info, **kwargs):
        return Notification.objects.all()

schema = graphene.Schema(query=Query)
