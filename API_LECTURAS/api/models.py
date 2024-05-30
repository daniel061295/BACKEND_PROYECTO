from django.db import models

# Create your models here.
class Mediciones(models.Model):
    id_medicion = models.AutoField(primary_key=True)
    humedad = models.FloatField()
    id_nodo = models.IntegerField()
    id_sensor = models.IntegerField()
    temperatura = models.FloatField()
    date_time = models.DateTimeField(blank=True, null=True)


    class Meta:
        db_table = 'mediciones'