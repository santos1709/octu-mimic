import os
from datetime import datetime, timedelta
from glob import glob
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd
from keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler

from db.database import Database
from keras_anomaly_detection.library.convolutional import Conv1DAutoEncoder


class Model(Conv1DAutoEncoder):
    def __init__(self, data_source=None):
        super().__init__()
        self.create_flag = False
        self.train_data_size = 10
        self.extension = 'h5'
        self.models_dir = 'models'
        self.model_name = ''
        self.version = ''
        self.model_id = ''
        self.model_dir = ''
        self.model_path = ''
        self.data_source = data_source
        if data_source is not None:
            self.get_model_info()

    @staticmethod
    def _date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def set_create(self, flag=True):
        self.create_flag = flag

    def load_model(self, model_path=None):
        self.get_model_info()
        model_path = self.model_path
        model_path_dir = '/'.join(model_path.split('/')[:2])

        super().load_model(model_path_dir)

    @staticmethod
    def get_most_recent_file(path):
        files = glob(path)
        files.sort(reverse=False)
        return files[0]

    def get_config_file(self, model_dir_path=None):
        if model_dir_path is None:
            return self.get_most_recent_file(f'{self.model_dir}/*-config.npy')
        return f"{model_dir_path}/{self.version}_{self.model_name}-{self.model_id}-config.npy"

    def get_weight_file(self, model_dir_path=None):
        if model_dir_path is None:
            return self.get_most_recent_file(f'{self.model_dir}/*-weights.h5')
        return f"{model_dir_path}/{self.version}_{self.model_name}-{self.model_id}-weights.h5"

    def get_architecture_file(self, model_dir_path=None):
        if model_dir_path is None:
            return self.get_most_recent_file(f'{self.model_dir}/*-architecture.json')
        return f"{model_dir_path}/{self.version}_{self.model_name}-{self.model_id}-architecture.json"

    def update_model_dir(self, model_name):
        self.model_dir = f'{self.models_dir}/{model_name}'
        return self.model_dir

    def get_model_path(self):
        return f'{self.models_dir}/{self.model_name}-{self.model_id}/{self.version}_{self.model_name}-{self.model_id}' \
            f'.{self.extension}'

    def get_model_info(self):
        db = Database()
        model_info_df = db.read_db('model_info')
        model_info_df.where(cond=model_info_df.usr == self.data_source.user, inplace=True)
        model_info_df.where(cond=model_info_df.device == self.data_source.device, inplace=True)
        model = model_info_df.model.to_list()[0]

        self.model_name = model.split('-')[0]
        self.model_id = model.split('-')[1]
        self.version = model_info_df.version.to_list()[0]
        self.create_flag = model_info_df.create_flag.to_list()[0]
        self.model_dir = self.update_model_dir(model)
        self.model_path = self.get_model_path()

        return model, self.version, self.create_flag

    def generate_model_id(self):
        db = Database()
        self.model_id = str(uuid4()).split('-')[0]
        model = f"{self.model_name}-{self.model_id}"
        db.update(f"model_info", 'model',
                  model, 'token', self.data_source.token)
        self.update_model_dir(model)
        try:
            os.listdir(f"{self.models_dir}/{model}")
        except FileNotFoundError:
            Path(f'{os.getcwd()}/{self.models_dir}/{model}').mkdir(parents=True, exist_ok=True)

        return self.model_id

    def version_model(self):
        db = Database()
        self.version = datetime.now().strftime("%Y-%m-%d")
        db.update(f"model_info", 'version',
                  self.version, 'token', self.data_source.token)
        versions = len(glob(f'{self.model_dir}/*'))  # TODO: USE DB(?)

        if not versions == 0:
            self.version = f'{self.version}-v{int(versions - 2) + 1}'

        self.update_model_dir(f'{self.model_name}-{self.model_id}')

    @staticmethod
    def _fit_data(df):
        np_dataset = df.as_matrix()
        scaler = MinMaxScaler()
        return scaler.fit_transform(np_dataset)

    def detect_if_anomaly(self, data_obj):
        pd_dataset = pd.DataFrame({f'{data_obj.key}': f'{data_obj.value}'})
        np_dataset = self._fit_data(pd_dataset)
        anomaly_information = self.model.anomaly(np_dataset)

        for idx, (is_anomaly, dist) in enumerate(anomaly_information):
            return {str(dist): ('abnormal' if is_anomaly else 'normal')}

    def train_model(self):
        pd_dataset = self.data_source.compile_data(self.train_data_size)
        np_dataset = self._fit_data(pd_dataset)

        self.fit(np_dataset[:self.train_data_size, :],
                 model_dir_path=self.model_dir,
                 estimated_negative_sample_ratio=0.9)

        anomaly_information = self.anomaly(np_dataset[:self.train_data_size, :])
        for idx, (is_anomaly, dist) in enumerate(anomaly_information):
            print('# ' + str(idx) + ' is ' + ('abnormal' if is_anomaly else 'normal') + ' (dist: ' + str(dist) + ')')

        return self.model

    def fit(self, dataset, model_dir_path, batch_size=8, epochs=100, validation_split=0.1, *args, **kwargs):
        if self.create_flag is True:
            self.generate_model_id()
            self.version_model()
            return super().fit(dataset, self.model_dir, batch_size=8, epochs=100, validation_split=0.1, *args, **kwargs)

        self.load_model()
        self.version_model()
        input_timeseries_dataset = np.expand_dims(dataset, axis=2)
        weight_file_path = self.get_weight_file(model_dir_path=None)
        checkpoint = ModelCheckpoint(weight_file_path)
        history = self.model.fit(x=input_timeseries_dataset, y=dataset,
                                 batch_size=batch_size, epochs=epochs,
                                 verbose=self.VERBOSE, validation_split=validation_split,
                                 callbacks=[checkpoint])
        self.model.save_weights(self.get_weight_file(model_dir_path=self.model_dir))

        return history
