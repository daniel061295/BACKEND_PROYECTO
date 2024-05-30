import time
import paho.mqtt.client as paho
from paho import mqtt



client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
node = 0
topic_trigger = 'SHM_PROYECTO/TRIGGER'
grid_status = {
    "0":"OFFLINE",
    "1":"OFFLINE",
    "2":"OFFLINE",
    "3":"OFFLINE",
    "4":"OFFLINE",
    "5":"OFFLINE",
    "6":"OFFLINE",
    "7":"OFFLINE",
    "8":"OFFLINE",
    "9":"OFFLINE"
    }
def get_topic_status_request (node): 
    return f'SHM_PROYECTO/STATUS/{node}/REQUEST'
def get_topic_status_response (node): 
    return f'SHM_PROYECTO/STATUS/{node}/RESPONSE'



# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    #print("mid: " + str(mid))
    pass

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    if msg.topic.startswith('SHM_PROYECTO/STATUS/'):
        # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))  
        node = int(msg.topic.split('/')[2])
        if msg.topic.startswith(get_topic_status_response(node)):
            grid_status[f"{node}"] = "ONLINE"
            #print(grid_status)
        # print(f'llego un mensaje en el nodo {node}')
    
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def init_mqtt(client=client):
    # using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
    # userdata is user defined data of any type, updated by user_data_set()
    # client_id is the given name of the client
    # print("iniciando")
    # client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set("danielcardenaz", "Manzana2132881")
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect("a33454d332054780b8feaf83950ed54a.s2.eu.hivemq.cloud", 8883)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish

    # subscribe to all topics of encyclopedia by using the wildcard "#"
    client.subscribe('SHM_PROYECTO/#', qos=0)

    # a single publish, this can also be done in loops, etc.
    # client.publish(topic, payload=message, qos=0)

    # loop_forever for simplicity, here you need to stop the loop manually
    # you can also use loop_start and loop_stop
    print("iniciando loopmqtt")
    client.loop_start()
    # client.loop_stop()
    # client.loop_forever()


def publish_message(topic, message, client=client, ):
    # client.loop_start()
    client.publish(topic, payload=message, qos=0)
    # client.loop_stop()
    
def publish_time_interval(message):
    publish_message(topic_trigger,message)

def update_status():
    for node in grid_status:
        grid_status[node] = "OFFLINE"
        publish_message(get_topic_status_request(node),"STATUS")

def get_status():
    update_status()
    time.sleep(2)
    return grid_status

