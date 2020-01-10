import glob
import os
from datetime import datetime, timedelta
from uuid import uuid4

import cv2
from imageai.Detection import ObjectDetection
from imageai.Prediction.Custom import ModelTraining

import config
from db.database import Database


class Model():
    def __init__(self):
        super().__init__()
        # self.train_data_size = 10
        self.model_name = ''
        self.version = ''
        self.user = ''
        self.model_id = ''
        self.model = None

    @staticmethod
    def _date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @staticmethod
    def get_most_recent_model(path):
        files = glob.glob(os.path.join(path, '*'))
        files.sort(reverse=False)
        return files[0].split(path)[-1]

    def select_model(self, user, name=None, version=None, model_id=None):
        db = Database()

        if not name:
            name = self.model_name
        db.update(
            table='models',
            column='name',
            value=name,
            where_col='usr',
            where_val=user
        )

        if not version:
            version = self.version
        db.update(
            table='models',
            column='version',
            value=version,
            where_col='usr',
            where_val=user
        )

        if not model_id:
            model_id = self.model_id
        db.update(
            table='models',
            column='id',
            value=model_id,
            where_col='usr',
            where_val=user
        )

        self.get_model_info(user)

    def load_model(self, user, model_path=None, update_db=False):
        if model_path:
            name = model_path.split('/')[0]
            version = model_path.split('_')[0]
            model_id = model_path.split('_')[1]
            if update_db:
                self.select_model(user=user, name=name, version=version, model_id=model_id)
        else:
            self.get_model_info(user)
            model_path = os.path.join(self.model_name, f'{self.version}_{self.model_id}.h5')

        model = ObjectDetection()
        model.setModelTypeAsRetinaNet()
        model.setModelPath(os.path.join(config.TRAIN_PATH, model_path))
        model.loadModel()

        return model

    def get_model_info(self, user, model=None):
        self.user = user
        if model:
            self.version = model.split('_')[0]
            self.model_name = model.split('/')[0]
            self.model_id = model.split('_')[1]
        else:
            db = Database()
            models_df = db.read_db('models')
            models_df.where(cond=models_df.usr == user, inplace=True)
            self.version = models_df.version.tolist()[0]
            self.model_name = models_df.name.tolist()[0]
            self.model_id = models_df.id.tolist()[0]

    def generate_model_id(self, user):
        db = Database()
        self.model_id = str(uuid4()).split('-')[0]
        db.update(
            table='models',
            column='id',
            value=self.model_id,
            where_col='usr',
            where_val=user
        )

    def version_model(self, user, name):
        self.version = datetime.now().strftime("%Y-%m-%d-%h-%M-%s")
        self.generate_model_id(user)
        self.select_model(user=user, name=name)

    def train_model(self, data_dir, user, new_model=False):
        # TODO: Test
        # https://towardsdatascience.com/train-image-recognition-ai-with-5-lines-of-code-8ed0bdd8d9ba
        if new_model:
            model_trainer = ModelTraining()
            model_trainer.setModelTypeAsResNet()
        else:
            model_trainer = self.load_model(user=user)

        model_trainer.setDataDirectory(data_dir)
        model_trainer.trainModel(
            num_objects=10,
            num_experiments=200,
            enhance_data=True,
            batch_size=32,
            show_network_summary=True
        )

        if new_model:
            self.version_model(user=user, name=data_dir.split('/')[-2])
        self.model = model_trainer
        return self.model

    def detect(self, user, picture_name, model=None):
        # TODO: Test
        # https://towardsdatascience.com/object-detection-with-10-lines-of-code-d6cb4d86f606
        detector = self.load_model(user, model)

        pic_path = os.path.join(config.INPUT_IMAGES_PATH, picture_name)
        detections = detector.detectObjectsFromImage(
            input_image=pic_path,
            output_image_path=os.path.join(config.OUTPUT_IMAGES_PATH, picture_name)
        )

        timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d-%h-%M-%s')
        last_untrained_dir = ''.join(timestamp.split('-'))
        image = cv2.imread(pic_path)
        results = dict()
        for obj_idx, obj in enumerate(detections):
            crop_img = image[
               detections[obj_idx]['box_points'][1]:detections[obj_idx]['box_points'][3],
               detections[obj_idx]['box_points'][0]:detections[obj_idx]['box_points'][2]
            ]

            detection_path = os.path.join(
                config.UNTRAINED_IMAGES_PATH,
                last_untrained_dir,
                obj["name"],
                f'{timestamp}.png'
            )
            cv2.imwrite(detection_path, crop_img)
            results[obj["name"]] = obj["percentage_probability"]

        return results, last_untrained_dir
