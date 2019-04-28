import os
from sys import modules
from datetime import datetime, timedelta
from uuid import uuid4

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from keras_anomaly_detection.library.convolutional import Conv1DAutoEncoder

from data_scanner import DataScanner


class Model(Conv1DAutoEncoder):
    def __init__(self):
        super().__init__()
        self.train_data_size = 20
        self.model_name = 'anomaly_model'
        self.extension = 'h5'
        self.models_dir = 'models'
        self.version = self.get_last_model()[0].split('_')[0]
        self.model_path = self.get_model_path()
        # self.model = self.update_model()

    @staticmethod
    def _date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @staticmethod
    def _fit_data(df):
        np_dataset = df.as_matrix()
        scaler = MinMaxScaler()
        return scaler.fit_transform(np_dataset)

    def get_model_path(self):
        return f'{self.models_dir}/{self.version}_{self.model_name}.{self.extension}'

    def get_last_model(self):
        files = os.listdir(self.models_dir)
        files.sort(reverse=True)

        return files[0]

    def update_model(self):
        self.load_model(self.model_path)

        return self.model

    def save_model(self, model):
        self.version = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        model.save(self.model_path)

    def detect_if_anomaly(self, data_obj):
        pd_dataset = pd.DataFrame({f'{data_obj.key}': f'{data_obj.value}'})
        np_dataset = self._fit_data(pd_dataset)
        anomaly_information = self.model.anomaly(np_dataset)

        for idx, (is_anomaly, dist) in enumerate(anomaly_information):
            return {str(dist): ('abnormal' if is_anomaly else 'normal')}

    def train_model(self):
        data_storage = DataScanner()
        pd_dataset = pd.DataFrame()

        data_files = data_storage.get_most_recents(self.train_data_size)
        for file in data_files:
            pd_dataset = pd.concat([pd_dataset, pd.read_csv(file)])

        data_storage.token = str(uuid4()).replace('-', '')
        pd_dataset.to_csv(f'{data_storage.data_full_path}')
        np_dataset = self._fit_data(pd_dataset)

        self.fit(np_dataset[:self.train_data_size, :],
                 model_dir_path=self.model_path,
                 estimated_negative_sample_ratio=0.9)

        for file in data_files:
            os.unlink(file)

        return self.model
