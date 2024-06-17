from .schema import schema
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from graphene_django.views import GraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("graphql/", GraphQLView.as_view(graphiql=settings.DEBUG, schema=schema)),
]
