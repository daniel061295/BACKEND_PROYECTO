#
# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import time
import paho.mqtt.client as paho
from paho import mqtt
import json
import requests
# from ..api.models import Mediciones as Medidas
from datetime import datetime



# conn = mysql.connector.connect(host="127.0.0.1",user="root",passwd="Manzana2132881+",database="proyecto")
topic = 'SHM_PROYECTO/#'


def upload_message (data):
    if data:
        for element in data:

            print(element)
            try:
                fechahora = str(element["fecha"])
                nodo = int(element["nodo"])
                temperatura = float(element["temperatura"])
                humedad = float(element["humedad"])

                body = {
                    "date_time" : datetime.strptime(fechahora, '%Y-%m-%d %H:%M:%S'),
                    "id_nodo" : nodo,
                    "temperatura" : temperatura,
                    "humedad" : humedad,
                    "id_sensor" : 1

                }
                response = requests.post(url="http://localhost:8000/data_collector/withvalidations/", data = body)
                if (response.status_code == 400):
                    print(response.text)
                    # time.sleep(0.5)
                if (response.status_code == 200):
                    print("MEDICION GUARDADA CON EXITO!")
            except Exception as e:
                print(f"El mensaje no cumple con el formato requerido\ne>{e}")

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    if rc == 0:
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.on_publish = on_publish
    else:
        print('Bad connection. Code:', rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    # print("mid: " + str(mid))
    pass

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
last_message= ''
def on_message(client, userdata, msg):
    global  last_message
    if  msg.topic.startswith('SHM_PROYECTO/MEDICIONES'):
        try:
            message = msg.payload.decode('utf8').replace("'", '"')
            if message != last_message:
                data = json.loads(message)
                upload_message(data)
                last_message = message
            else:
                print("MENSAJE REPETIDO")
        except Exception as e:
            print(f"Error leyendo json:{e}")
    else:
        # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        pass
if __name__ == "__main__":
    # using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
    # userdata is user defined data of any type, updated by user_data_set()
    # client_id is the given name of the client
    client = paho.Client(client_id="1", userdata=None, protocol=paho.MQTTv31)
    client.on_connect = on_connect

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set("danielcardenaz", "Manzana2132881")
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect("a33454d332054780b8feaf83950ed54a.s2.eu.hivemq.cloud", 8883)

    # setting callbacks, use separate functions like above for better visibility


    # subscribe to all topics of encyclopedia by using the wildcard "#"
    client.subscribe(topic, qos=0)

    # a single publish, this can also be done in loops, etc.
    #client.publish("encyclopedia/temperature", payload="hot", qos=1)

    # loop_forever for simplicity, here you need to stop the loop manually
    # you can also use loop_start and loop_stop
    client.loop_forever()
    # client.loop_start()