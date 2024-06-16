import graphene
from .models import CustomUser
from graphene_django.types import DjangoObjectType

class CustomUserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        interfaces = (graphene.relay.Node,)
        filter_fields = ['id', 'username', 'email', 'cpf', 'phone_number']
        fields = ('id', 'username', 'email', 'cpf', 'phone_number')

# Mutação para criar um novo CustomUser
class CreateCustomUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        cpf = graphene.String(required=True)
        phone_number = graphene.String(required=True)

    custom_user = graphene.Field(CustomUserType)
    success = graphene.Boolean()

    def mutate(self, info, username, email, cpf, phone_number):
        custom_user = CustomUser(username=username, email=email, cpf=cpf, phone_number=phone_number)
        custom_user.save()
        return CreateCustomUser(custom_user=custom_user, success=True)

# Mutação para atualizar um CustomUser existente
class UpdateCustomUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        username = graphene.String()
        email = graphene.String()
        cpf = graphene.String()
        phone_number = graphene.String()

    custom_user = graphene.Field(CustomUserType)
    success = graphene.Boolean()

    def mutate(self, info, id, username=None, email=None, cpf=None, phone_number=None):
        custom_user = CustomUser.objects.get(pk=id)
        if username:
            custom_user.username = username
        if email:
            custom_user.email = email
        if cpf:
            custom_user.cpf = cpf
        if phone_number:
            custom_user.phone_number = phone_number
        custom_user.save()
        return UpdateCustomUser(custom_user=custom_user, success=True)

# Mutação para deletar um CustomUser
class DeleteCustomUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        custom_user = CustomUser.objects.get(pk=id)
        custom_user.delete()
        return DeleteCustomUser(success=True)

# Agrupar todas as mutações relacionadas ao CustomUser em uma classe de Mutation
class Mutation(graphene.ObjectType):
    create_custom_user = CreateCustomUser.Field()
    update_custom_user = UpdateCustomUser.Field()
    delete_custom_user = DeleteCustomUser.Field()