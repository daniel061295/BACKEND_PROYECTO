from rest_framework import serializers
from .models import Mediciones
from django.contrib.auth.models import User

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password']

class DownloadCsvSerializer(serializers.Serializer):
    id_nodo = serializers.IntegerField()
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField()