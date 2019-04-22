import paho.mqtt.client as mqtt
import random
from time import sleep


topic = [
    "outTopic/potencia",
    "outTopic/vazao",
    "outTopic/tensao",
    "outTopic/corrente"
]


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for t in topic:
        client.subscribe(t)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('bwoigzxu', 'NvYmeI7tN46L')
client.connect("m13.cloudmqtt.com", 18869, 60)

while True:
    for t in topic:
        if t == 'outTopic/potencia':
            msg = str(random.randrange(350, 500))
        elif t == 'outTopic/vazao':
            msg = str(random.randrange(1, 5))
        elif t == 'outTopic/tensao':
            msg = str(random.randrange(114, 120))
        elif t == 'outTopic/corrente':
            msg = str(random.randrange(2, 8))

        client.publish(topic=t, payload=msg)
        print('Publishing ' + msg + ' in ' + t)
    sleep(5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()