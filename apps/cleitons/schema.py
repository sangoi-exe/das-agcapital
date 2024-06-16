import graphene
from .models import Cleiton
from django.db import transaction
from graphene_django.types import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

class CleitonType(DjangoObjectType):
    class Meta:
        model = Cleiton
        fields = '__all__' # sem campos sensíveis, utilizar todos

class CreateCleiton(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        phone = graphene.String()
        address = graphene.String()

    cleiton = graphene.Field(CleitonType)
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        try: # criar cleiton com tratamento de validação e erros
            with transaction.atomic(): # transação atômica para garantir a integridade da manipulação no banco
                cleiton = Cleiton(**kwargs)
                cleiton.full_clean() # validar antes de salvar
                cleiton.save()
            return CreateCleiton(cleiton=cleiton, success=True)
        except ValidationError as e:
            return CreateCleiton(cleiton=None, success=False, errors=str(e))

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
        try: # realizar update de cleiton com tratamento de validação e erros
            with transaction.atomic(): # transação atômica para garantir a integridade da manipulação no banco
                cleiton = Cleiton.objects.get(pk=id)
                for key, value in kwargs.items():
                    setattr(cleiton, key, value)  # Atualiza os campos do Cleiton.
                cleiton.full_clean()  # Valida as alterações antes de salvar.
                cleiton.save()
            return UpdateCleiton(cleiton=cleiton, success=True)
        except ObjectDoesNotExist:
            return UpdateCleiton(cleiton=None, success=False, errors="Cleiton not found.")
        except ValidationError as e:
            return UpdateCleiton(cleiton=None, success=False, errors=str(e))

class DeleteCleiton(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try: # deletar cleiton com tratamento de validação e erros
            with transaction.atomic(): # transação atômica para garantir a integridade da manipulação no banco
                cleiton = Cleiton.objects.get(pk=id)
                cleiton.delete()
            return DeleteCleiton(success=True)
        except ObjectDoesNotExist:
            return DeleteCleiton(success=False, errors="Cleiton not found.")

class Mutation(graphene.ObjectType):
    create_cleiton = CreateCleiton.Field()
    update_cleiton = UpdateCleiton.Field()
    delete_cleiton = DeleteCleiton.Field()