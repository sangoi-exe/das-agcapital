from rest_framework import serializers

from .models import Cleiton


class CleitonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cleiton
        fields = "__all__"
