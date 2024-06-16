import graphene
from .models import Cleiton
from graphene_django.types import DjangoObjectType

class CleitonType(DjangoObjectType):
    class Meta:
        model = Cleiton
        fields = '__all__'

class CreateCleiton(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        address = graphene.String()

    cleiton = graphene.Field(CleitonType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        cleiton = Cleiton(**kwargs)
        cleiton.save()
        return CreateCleiton(cleiton=cleiton, success=True)

class UpdateCleiton(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        address = graphene.String()

    cleiton = graphene.Field(CleitonType)
    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        cleiton = Cleiton.objects.get(pk=id)
        for key, value in kwargs.items():
            setattr(cleiton, key, value)
        cleiton.save()
        return UpdateCleiton(cleiton=cleiton, success=True)

class DeleteCleiton(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        cleiton = Cleiton.objects.get(pk=id)
        cleiton.delete()
        return DeleteCleiton(success=True)

class Mutation(graphene.ObjectType):
    create_cleiton = CreateCleiton.Field()
    update_cleiton = UpdateCleiton.Field()
    delete_cleiton = DeleteCleiton.Field()