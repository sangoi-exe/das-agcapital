from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CleitonViewSet

router = DefaultRouter()
router.register(r"cleiton", CleitonViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
