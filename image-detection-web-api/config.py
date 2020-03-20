import os

WORKING_DIR = os.getcwd()

DB = {
    "DB_NAME": "postgres",
    "PORT": "6381",
    "USERNAME": "postgres",
    "PASSWORD": "",
    "HOST": "10.152.183.95"
}

# DATA_PATH = f'{WORKING_DIR}/data'
# MODELS_PATH = f'{DATA_PATH}''/{}''/models'
# PICS_PATH = f'{WORKING_DIR}/data/pictures'

DATA_PATH = os.environ.get('DATA_PATH')
MODELS_PATH = os.environ.get('MODELS_PATH')
PICS_PATH = os.environ.get('PICS_PATH')

INPUT_IMAGES_PATH = PICS_PATH
OUTPUT_IMAGES_PATH = f'{PICS_PATH}/output'

HOST = 'http://127.0.0.1'
PORT = '8880'
HOST_NAME = f'{HOST}:{PORT}'

EVALUATE_ROUTE = '/data/evaluate'
VALIDATE_ROUTE = '/data/validate'
TRAIN_ROUTE = '/model/train'
SELECT_ROUTE = '/model/select'
LIST_ROUTE = '/model/list'
