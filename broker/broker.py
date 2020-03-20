import paho.mqtt.client as mqtt
import requests

import config
from data_scanner import DataScanner


def save_data(image, user, device_name, operator):
    """
    Save the receive data and send a http request to the web server with the saved image information

    Args:
        image (bytearray): bytes array data object of the png image
        user (str): registered user
        device_name (str): name of the device whereas the data came from
        operator (str): name of the operator that interacted with the device whereas data came from
    """
    data = DataScanner()
    img_path = data.save_picture(serialized_file=image, user=user, device_name=device_name)

    json_data = {
        "user": user,
        "picture": img_path,
        "device_name": device_name,
        "operator": operator
    }

    ret = requests.post(config.EVALUATE_ROUTE, data=json_data)
    print(ret.content)


def on_connect(client, userdata, flags, rc):
    """
    The callback for when the client receives a CONNACK response from the server.
    Subscribing in on_connect() means that if we lose the connection and
    reconnect then subscriptions will be renewed.

    Args:
        client (object): the client instance for this callback
        userdata (object): private user data as set in Client() or user_data_set()
        flags (dict): response flags sent by the broker
        rc (int): connection result
    """
    print(f"Connected with result code {rc}")
    for t in config.TOPICS:
        client.subscribe(t)


def on_message(client, userdata, msg):
    """
    The callback for when a PUBLISH message is received from the server.

    Args:
        client (object): the client instance for this callback
        userdata (object): private user data as set in Client() or user_data_set()
        msg (object): message payload, an instance of MQTTMessage.
            This is a class with members topic, payload, qos, retain.
    """
    print(f'{msg.topic} {type(msg.payload)}')
    topic_levels = msg.topic.split('/')
    user = topic_levels[1]
    device_name = topic_levels[2]
    operator = topic_levels[3]
    image = msg.payload

    save_data(image=image, user=user, device_name=device_name, operator=operator)


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
