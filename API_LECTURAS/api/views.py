from .models import Mediciones
from .serializers import MedicionesSerializer, GetMedicionBetweenRangeSerializer, GetLast, UserSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import api_view , authentication_classes, permission_classes
from rest_framework.response import Response
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import json



class MedicionesViewSet(viewsets.ModelViewSet):
    queryset = Mediciones.objects.all()
    serializer_class = MedicionesSerializer

@api_view(['POST'])
def post_medicion_with_validations(request):
    if request.method == 'POST':
        serializer = MedicionesSerializer(data=request.data)
        if serializer.is_valid():
            nodo = serializer.validated_data["id_nodo"]
            fechahora = serializer.validated_data["date_time"]
            temperatura = serializer.validated_data["temperatura"]
            humedad = serializer.validated_data["humedad"]
            if list(Mediciones.objects.filter(date_time=fechahora,
                                        id_nodo=nodo).values_list()):
                return Response({"detail":"MEDICION REPETIDA, NO SE GUARDARA EN LA DB!"},status=status.HTTP_400_BAD_REQUEST)
            if temperatura == humedad == 0:
                return Response({"detail": "MEDICION INVALIDA"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
        else:
            return Response({"detail":"NO PASO VALIDACIONES",
                             "errors":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
#
@api_view(['POST'])
def get_medicion_between_range(request):
    if request.method == 'POST':
        serializer = GetMedicionBetweenRangeSerializer(data=request.data)
        if serializer.is_valid():
            nodo = serializer.validated_data["id_nodo"]
            fecha_inicio = serializer.validated_data["fecha_inicio"]
            fecha_fin = serializer.validated_data["fecha_fin"]

            records = Mediciones.objects.filter(id_nodo=nodo,date_time__gte=fecha_inicio, date_time__lte=fecha_fin)
            response = serializers.serialize('json', records)

            response = json.loads(response)

            if not response:
                return Response([], status=status.HTTP_200_OK)
            else:
                response = [response[i]["fields"] for i in range(len(response))]
                if len(response)>48:
                    response = response[-48:]
                return Response(response,status=status.HTTP_200_OK)
        else:
            print(request.data)
            return Response({"detail": "NO PASO VALIDACIONES",
                             "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def get_last(request):
    if request.method == 'POST':
        serializer = GetLast(data=request.data)
        if serializer.is_valid():
            nodo = serializer.validated_data["id_nodo"]
            records = Mediciones.objects.filter(id_nodo=nodo).last()
            response = serializers.serialize('json', [records])
            response = json.loads(response)

            if not response:
                #return Response(
                 #   {"detail": f"NO SE ENCONTRARON MEDICIONES PARA EL NODO {nodo} "},
                 #   status=status.HTTP_400_BAD_REQUEST)
                return Response([], status=status.HTTP_200_OK)
            else:
                response = [response[i]["fields"] for i in range(len(response))]
                return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "NO PASO VALIDACIONES",
                             "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User,username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({'error':'Invalid password'},status=status.HTTP_400_BAD_REQUEST)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token":token.key,"user":serializer.data},status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token':token.key, 'user':serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
