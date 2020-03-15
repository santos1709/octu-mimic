import os

WORKING_DIR = os.getcwd()

TOPICS = ["outTopic/+/+/+/#"]

# MQTT broker info
USER = "mosquitto"
PASS = ""
HOST = "10.152.183.95"
PORT = "6380"

# Main webapp infos
WEBAPP = "10.152.183.42:6379"
PICS_PATH = f'{WORKING_DIR}/../app/data'
