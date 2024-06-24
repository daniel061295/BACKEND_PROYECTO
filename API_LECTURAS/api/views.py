from .models import Mediciones
from .serializers import MedicionesSerializer, GetMedicionBetweenRangeSerializer, GetLast, UserSerializer, DownloadCsvSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import api_view , authentication_classes, permission_classes, action
from rest_framework.response import Response
from django.core import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
import json
from django.http import HttpResponse
import csv
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt


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
                respuesta = []
                for medida in response:
                    meta_data = medida["fields"]
                    medida_dict = {}
                    fecha_ = meta_data["date_time"].split(':')
                    medida_dict["date_time"] = fecha_[0] + ":" + fecha_[1]
                    medida_dict["temperatura"] = meta_data["temperatura"]
                    medida_dict["humedad"] = meta_data["humedad"]
                    respuesta.append(medida_dict)

                if len(respuesta)>48:
                    respuesta = respuesta[-48:]
                print(respuesta)
                return Response(respuesta,status=status.HTTP_200_OK)
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
                fecha_ = response[0]["date_time"].split(':')
                response[0]["date_time"] = fecha_[0]+":"+fecha_[1]
                # print(response[0]["date_time"])
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

# @csrf_exempt
# @action(detail=False, methods=['post'])
@api_view(['POST'])
def download_csv(request):
    if not(request.method )== 'POST':
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = DownloadCsvSerializer(data=request.data)
    if not(serializer.is_valid()):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    nodo = serializer.validated_data["id_nodo"]
    fecha_inicio = serializer.validated_data["fecha_inicio"]
    fecha_fin = serializer.validated_data["fecha_fin"]

    records = Mediciones.objects.filter(id_nodo=nodo, date_time__gte=fecha_inicio, date_time__lte=fecha_fin)
    data = serializers.serialize('json', records)
    data = json.loads(data)
    if not data:
        return Response({'details':"No se encontraron datos entre las fechas estipuladas"},status=status.HTTP_400_BAD_REQUEST)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="datos.csv"'
    writer = csv.DictWriter(response, fieldnames=['Id_nodo', 'Fecha hora', 'Temperatura', 'Humedad'])
    writer.writeheader()
    for i in data:
        meta_data = i["fields"]
        detail_dict = {}
        detail_dict["Id_nodo"] = meta_data["id_nodo"]
        detail_dict["Fecha hora"] = meta_data["date_time"]
        detail_dict["Temperatura"] = meta_data["temperatura"]
        detail_dict["Humedad"] = meta_data["humedad"]
        writer.writerow(detail_dict)
    return response
