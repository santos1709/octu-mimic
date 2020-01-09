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
        self.name = 'imageAI0'
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

    def select_model(self, user, name=None, version=None):
        if not name and not version:
            name = self.model_name
            version = self.version

        db = Database()
        db.update(
            table='models',
            column='name',
            value=name,
            where_col='user',
            where_val=user
        )
        db.update(
            table='models',
            column='version',
            value=version,
            where_col='user',
            where_val=user
        )

    def load_model(self, user, model_filename=None, update_db=False):
        if model_filename:
            name = model_filename.split('_')[1]
            version = model_filename.split('_')[0]
            if update_db:
                self.select_model(user=user, name=name, version=version)
        else:
            self.get_model_info(user)
            model_filename = f'{self.version}_{self.model_name}.h5'

        model = ObjectDetection()
        model.setModelTypeAsRetinaNet()
        model.setModelPath(os.path.join(config.MODELS_PATH, model_filename))
        model.loadModel()

        return model

    def get_model_info(self, user, model=None):
        if not model:
            db = Database()
            models_df = db.read_db('models')
            models_df.where(cond=models_df.usr == user, inplace=True)
            model = models_df.version.tolist()[0]

        self.user = user
        self.version = model.split('_')[0]
        self.model_name = model.split('_')[1]
        # self.model_id = model.split('-')[2] # TODO: Evaluate if necessary

    def generate_model_id(self, user):
        db = Database()
        self.model_id = str(uuid4()).split('-')[0]
        model = f"{self.name}-{self.model_id}"
        db.update(
            table='models',
            column='model',
            value=model,
            where_col='user',
            where_val=user
        )

    def version_model(self, user):
        self.version = datetime.now().strftime("%Y-%m-%d-%h-%M-%s")

        db = Database()
        db.update(
            table='models',
            column='version',
            value=self.version,
            where_col='user',
            where_val=user
        )

    def train_model(self, data_dir, user=None):
        # TODO: Test
        # https://towardsdatascience.com/train-image-recognition-ai-with-5-lines-of-code-8ed0bdd8d9ba
        if user:
            model_trainer = self.load_model(user=user)
        else:
            model_trainer = ModelTraining()
            model_trainer.setModelTypeAsResNet()

        model_trainer.setDataDirectory(data_dir)
        model_trainer.trainModel(
            num_objects=10,
            num_experiments=200,
            enhance_data=True,
            batch_size=32,
            show_network_summary=True
        )

        self.version_model(user)
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
