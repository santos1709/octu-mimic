import os
import pickle
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import config


class DataScanner:
    def __init__(self):
        self.timestamp = ''
        self.user = ''
        self.device_name = ''
        self.data_path = ''
        self.uid = ''
        self.pic = ''
        self.model_version = ''
        self.model_name = ''
        self.model_id = ''
        self.last_untrained = ''
        self.new_model = ''
        self.operator = ''

    def iter_files(self):
        files_path = os.path.join(config.PICS_PATH, self.device_name)

        try:
            os.listdir(files_path)
        except FileNotFoundError:
            Path(os.path.join(os.getcwd(), files_path)).mkdir(parents=True, exist_ok=True)
        finally:
            data_files = os.listdir(files_path)

        data_files.sort(key=len)
        for file in data_files:
            file = os.path.join(files_path, file)
            self.timestamp = file.split('/')[-1].split('_')[0]
            self.uid = file.split('/')[-1].split('_')[-1]
            self.device_name = file.split('/')[-2]
            yield file

    @staticmethod
    def deserialize(serialized_file_path):
        with open(serialized_file_path, 'r') as f:
            deserialized_file = pickle.load(f)

        return deserialized_file

    @staticmethod
    def save_serialized(serialized_file, user, device_name):
        uid = str(uuid4()).split('-')[0]
        timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d-%h-%M-%s')

        file_path = os.path.join(config.PICS_PATH, user, device_name, f'{timestamp}_{uid}')
        with open(file_path, 'w+') as f:
            f.write(serialized_file)

    def save_picture(self, serialized_file_path):
        image_file = self.deserialize(serialized_file_path)

        image_path = f'{serialized_file_path}.png'
        with open(image_path, 'w+') as f:
            f.write(image_file)
