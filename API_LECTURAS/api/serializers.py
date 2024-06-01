from rest_framework import serializers
from .models import Mediciones

class MedicionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mediciones
        fields = '__all__'

class GetMedicionBetweenRangeSerializer(serializers.Serializer):
    id_nodo = serializers.IntegerField()
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField()

class GetLast(serializers.Serializer):
    id_nodo = serializers.IntegerField()