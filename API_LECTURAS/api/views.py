from rest_framework import viewsets
from .models import Mediciones
from .serializers import MedicionesSerializer, GetMedicionBetweenRangeSerializer, GetLast
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core import serializers
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
                return Response({"detail":f"NO SE ENCONTRARON MEDICIONES PARA EL NODO {nodo} ENTRE {fecha_inicio} Y {fecha_fin}"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = [response[i]["fields"] for i in range(len(response))]
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
                return Response(
                    {"detail": f"NO SE ENCONTRARON MEDICIONES PARA EL NODO {nodo} "},
                    status=status.HTTP_400_BAD_REQUEST)
            else:
                response = [response[i]["fields"] for i in range(len(response))]
                return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "NO PASO VALIDACIONES",
                             "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)