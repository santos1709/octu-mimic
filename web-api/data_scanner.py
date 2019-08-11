import os
from pathlib import Path


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

    def update_path(self):
        self.data_path = f'data/{self.user}/{self.device}'

    def update_full_path(self):
        self.data_full_path = f'{self.data_path}/{self.timestamp}_{self.key}_{self.partial_token}.csv'

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
