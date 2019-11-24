import paho.mqtt.client as mqtt
import random
import time
import requests
import config
from db import Database


def save_data(msg)
    token = db.select('token', config.MODEL_TABLE, 'user', config.USER)
    json_data = {
            "user": config.USER,
            "device": config.DEVICE,
            "key": msg.payload.split('-')[0],
            "value": msg.payload.split('-')[-1],
            "token": token,
            "timestamp": time.strftime('%Y-%m-%d', time.localtime())
            }
    requests.post(f"{config.WEBAPP}/data/send", data=json_data)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for t in config.TOPICS:
        client.subscribe(t)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f'{msg.topic} {msg.payload}') 
    save_data(msg)


if __name__ == "main":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    # client.username_pw_set('bwoigzxu', 'NvYmeI7tN46L')
    # client.connect("m13.cloudmqtt.com", 18869, 60)
    client.username_pw_set(config.USER, config.PASS)
    client.connect(config.HOST, config.PORT, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
