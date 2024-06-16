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

    def mutate(self, info, name, email, phone, address):
        cleiton = Cleiton(name=name, email=email, phone=phone, address=address)
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

    def mutate(self, info, id, name=None, email=None, phone=None, address=None):
        cleiton = Cleiton.objects.get(pk=id)
        if name:
            cleiton.name = name
        if email:
            cleiton.email = email
        if phone:
            cleiton.phone = phone
        if address:
            cleiton.address = address
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