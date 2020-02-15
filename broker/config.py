import os

WORKING_DIR = os.getcwd()

TOPICS = ["outTopic/+/+/+/#"]

# MQTT broker info
USER = "mosquitto"
PASS = ""
HOST = "192.168.122.212"
PORT = "1883"

# MQTT test broker info
# USER = 'bwoigzxu'
# PASS = "NvYmeI7tN46L"
# HOST = "m13.cloudmqtt.com"
# PORT = "18869"

# Main webapp infos
WEBAPP = "192.168.122.66:6379"
PICS_PATH = f'{WORKING_DIR}/../image-detection-web-api/data'
