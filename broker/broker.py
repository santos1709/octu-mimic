import json

import paho.mqtt.client as mqtt
import requests

import config
from data_scanner import DataScanner


def save_data(image_serialized, prj, user, device_name, operator):
    data = DataScanner()
    img_path = data.save_picture(serialized_file=image_serialized, prj=prj, user=user, device_name=device_name)

    json_data = {
        "user": user,
        "picture": img_path,
        "device_name": device_name,
        "operator": operator
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
    print(f'{msg.topic} {type(msg.payload)}')
    # msg_dict = json.loads(msg.payload.decode().replace("'", '"'))
    topic_levels = msg.topic.split('/')
    prj = topic_levels[1]
    user = topic_levels[2]
    device_name = topic_levels[3]
    operator = topic_levels[4]
    image = msg.payload

    save_data(image_serialized=image, prj=prj, user=user, device_name=device_name, operator=operator)


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set(config.USER, config.PASS)
    client.connect(config.HOST, int(config.PORT), 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
