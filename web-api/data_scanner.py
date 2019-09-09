import os
from pathlib import Path
from uuid import uuid4

import pandas as pd


class DataScanner:
    def __init__(self):
        self.key = ''
        self.value = ''
        self.token = ''
        self.partial_token = ''
        self.timestamp = ''
        self.model_name = ''
        self.model_version = ''
        self.user = ''
        self.device = ''
        self.data_path = ''
        self.data_full_path = ''

    def generate_path(self, user=None, device=None):
        user = self.user if user is None else user
        device = self.device if device is None else user

        self.data_path = f'data/{user}/{device}'
        return self.data_path

    def generate_full_path(self, data_path=None, timestamp=None, key=None, token=None):
        data_path = self.data_path if data_path is None else data_path
        timestamp = self.timestamp if timestamp is None else timestamp
        key = self.key if key is None else key
        token = self.partial_token if token is None else token

        self.data_full_path = f'{data_path}/{timestamp}_{key}_{token}.csv'
        return self.data_full_path

    def iter_files(self):
        try:
            os.listdir(self.data_path)
        except FileNotFoundError:
            Path(f'{os.getcwd()}/{self.data_path}').mkdir(parents=True, exist_ok=True)
        finally:
            data_files = os.listdir(self.data_path)

        data_files.sort(key=len)
        for file in data_files:
            file = f'{self.data_path}/{file}'
            self.key = file.split('_')[1]
            self.partial_token = file.split('_')[-1].split('.')[0]
            self.timestamp = file.split('_')[0].split('/')[-1]
            self.user = file.split('/')[1]
            self.device = file.split('/')[2]
            yield file

    def get_most_recents(self, size=None):
        top_size = []
        if size is None:
            for file in self.iter_files():
                if len(self.partial_token) < 13:
                    top_size.append(file)
                    continue
                return top_size
        else:
            for length, file in enumerate(self.iter_files()):
                if length < size:
                    top_size.append(file)
                    continue
                return top_size
        return top_size

    def compile_data(self, data_size=None):
        pd_dataset = pd.DataFrame()

        data_files = self.get_most_recents(data_size)  # TODO: Validate this
        for file in data_files:
            pd_dataset = pd.concat([pd_dataset, pd.read_csv(file, header=None)])

        pd_dataset = pd_dataset.drop(11, axis=1)
        last_value = pd_dataset[0].tail(1)[0]
        pd_dataset = pd_dataset.head(pd_dataset[0].count() - 1)

        tmp_token = str(uuid4()).replace('-', '')
        pd_dataset.to_csv(f'{self.generate_full_path(token=tmp_token)}', header=None, index=False)

        for file in data_files:
            os.unlink(file)

        with open(f'{self.generate_full_path(token=self.token.split("-")[-1])}', 'a+') as file:
            file.write(str(last_value))
            file.write(',')

        return pd_dataset
