import graphene
from .models import Activity
from graphene_django.types import DjangoObjectType

class ActivityType(DjangoObjectType):
    class Meta:
        model = Activity
        interfaces = (graphene.relay.Node, )
        filter_fields = ['description', 'project', 'priority', 'status', 'creation_date', 'expected_completion_date']
        fields = '__all__'

class CreateActivity(graphene.Mutation):
    class Arguments:
        description = graphene.String(required=True)
        project = graphene.String(required=True)
        priority = graphene.String(required=True)
        status = graphene.String(required=True)
        creation_date = graphene.String(required=True)
        expected_completion_date = graphene.String(required=True)

    activity = graphene.Field(ActivityType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        activity = Activity(**kwargs)
        activity.save()
        return CreateActivity(activity=activity, success=True)

class UpdateActivity(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        description = graphene.String()
        project = graphene.String()
        priority = graphene.String()
        status = graphene.String()
        creation_date = graphene.String()
        expected_completion_date = graphene.String()

    activity = graphene.Field(ActivityType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        activity = Activity.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(activity, key, value)
        activity.save()
        return UpdateActivity(activity=activity, success=True)

class DeleteActivity(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        activity = Activity.objects.get(pk=id)
        activity.delete()
        return DeleteActivity(success=True)

class Mutation(graphene.ObjectType):
    create_activity = CreateActivity.Field()
    update_activity = UpdateActivity.Field()
    delete_activity = DeleteActivity.Field()