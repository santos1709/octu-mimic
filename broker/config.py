import os

WORKING_DIR = os.getcwd()

# TOPICS = ["outTopic/+/+/+/#"]
TOPICS = os.environ.get('TOPICS').split(':')

# MQTT broker info
USER = "mosquitto"
PASS = ""
HOST = "10.152.183.112"
PORT = "6380"

# Main webapp infos
WEBAPP = "10.152.183.42:6379"
# PICS_PATH = f'{WORKING_DIR}/../app/data'
PICS_PATH = os.environ.get('PICS_PATH')

EVALUATE_ROUTE = f'{WEBAPP}/{os.environ.get("EVALUATE_ROUTE")}'
VALIDATE_ROUTE = f'{WEBAPP}/{os.environ.get("VALIDATE_ROUTE")}'
TRAIN_ROUTE = f'{WEBAPP}/{os.environ.get("TRAIN_ROUTE")}'
SELECT_ROUTE = f'{WEBAPP}/{os.environ.get("SELECT_ROUTE")}'
LIST_ROUTE = f'{WEBAPP}/{os.environ.get("LIST_ROUTE")}'
