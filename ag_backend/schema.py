import graphene
from apps.cleitons.schema import CleitonType, CreateCleiton, UpdateCleiton, DeleteCleiton
from apps.accounts.schema import CustomUserType, CreateCustomUser, UpdateCustomUser, DeleteCustomUser
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from django.contrib.auth import get_user_model

''' refatorando para schemas locais
class DocumentType(DjangoObjectType):
    class Meta:
        model = Document
        interfaces = (graphene.relay.Node, )
        filter_fields = ['name', 'file', 'uploaded_at', 'project']
        fields = '__all__'

class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        interfaces = (graphene.relay.Node, )
        filter_fields = ['recipient', 'title', 'message', 'created_at', 'read', 'read_at']
        fields = '__all__'

class ProjectType(DjangoObjectType):
    class Meta:
        model = Project
        interfaces = (graphene.relay.Node, )
        filter_fields = ['name', 'description', 'cleiton', 'status', 'start_date', 'estimated_end_date']
        fields = '__all__'

class ReportType(DjangoObjectType):
    class Meta:
        model = Report
        interfaces = (graphene.relay.Node, )
        filter_fields = ['title', 'content', 'generated_at', 'project']
        fields = '__all__'

class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        interfaces = (graphene.relay.Node, )
        filter_fields = ['title', 'description', 'due_date', 'completed', 'project', 'activity']
        fields = '__all__'
'''

class Query(graphene.ObjectType):    
    user = graphene.Field(CustomUserType, user_id=graphene.Int())
    all_users = DjangoFilterConnectionField(CustomUserType)
    all_clients = DjangoFilterConnectionField(CleitonType)

class Mutation(graphene.ObjectType):
    create_cleiton = CreateCleiton.Field()
    update_cleiton = UpdateCleiton.Field()
    delete_cleiton = DeleteCleiton.Field()
    
    create_custom_user = CreateCustomUser.Field()
    update_custom_user = UpdateCustomUser.Field()
    delete_custom_user = DeleteCustomUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
