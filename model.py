import os

from datetime import datetime, timedelta
from keras.models import load_model


class Model:
    def __init__(self):
        self.batch_size = 256
        self.epochs = 10
        self.model_name = 'anomaly_model'
        self.extension = 'h5'
        self.version = self.get_last_model().split('_')[0]
        self.model = load_model('models/{}'.format(self.get_last_model()))

    @staticmethod
    def get_last_model():
        files = os.listdir('models/')
        files.sort(reverse=True)

        return files[0]

    @staticmethod
    def _date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def update_model(self):
        self.model = load_model(f'models/{self.version}_{self.model_name}.{self.extension}')

        return self.model

    def save_model(self, model):
        now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        model.save('models/{}.{}'.format(self.model_name, now, self.extension))

    def train_model(self, u, i, uv, iv, y):
        model = self.model
        return model.fit([u, i, uv, iv],
                         y,
                         batch_size=self.batch_size,
                         epochs=self.epochs,
                         verbose=1,
                         shuffle=True,
                         class_weight={0: .2, 1: 1})
