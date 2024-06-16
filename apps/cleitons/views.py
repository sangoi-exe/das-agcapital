from django.http import HttpResponse
from rest_framework import viewsets

from .models import Cleiton
from .serializers import CleitonSerializer


class CleitonViewSet(viewsets.ModelViewSet):
    queryset = Cleiton.objects.all()
    serializer_class = CleitonSerializer

    def hello_world(request):
        return HttpResponse("Hello World!", content_type="text/plain")
