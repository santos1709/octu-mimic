import glob
import os
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path

import cv2
from imageai.Detection.Custom import DetectionModelTrainer
from imageai.Detection.Custom import CustomObjectDetection
from lxml import etree
import xml.etree.cElementTree as ET

import config
from db.database import Database


class Model():
    def __init__(self):
        super().__init__()
        self.version = ''
        self.user = ''
        self.model_id = ''
        self.model_name = ''
        self.model_path = ''
        self.model = None

    @staticmethod
    def write_xml(img_path, objects, tl, br, savedir):
        if not os.path.isdir(savedir):
            os.mkdir(savedir)

        image = cv2.imread(img_path)
        height, width, depth = image.shape

        annotation = ET.Element('annotation')
        ET.SubElement(annotation, 'folder').text = '/' + os.path.join(*img_path.split('/')[:-1])
        ET.SubElement(annotation, 'filename').text = img_path.split('/')[-1]
        ET.SubElement(annotation, 'segmented').text = '0'
        size = ET.SubElement(annotation, 'size')
        ET.SubElement(size, 'width').text = str(width)
        ET.SubElement(size, 'height').text = str(height)
        ET.SubElement(size, 'depth').text = str(depth)
        for obj, topl, botr in zip(objects, tl, br):
            ob = ET.SubElement(annotation, 'object')
            ET.SubElement(ob, 'name').text = obj
            ET.SubElement(ob, 'pose').text = 'Unspecified'
            ET.SubElement(ob, 'truncated').text = '0'
            ET.SubElement(ob, 'difficult').text = '0'
            bbox = ET.SubElement(ob, 'bndbox')
            ET.SubElement(bbox, 'xmin').text = str(topl[0])
            ET.SubElement(bbox, 'ymin').text = str(topl[1])
            ET.SubElement(bbox, 'xmax').text = str(botr[0])
            ET.SubElement(bbox, 'ymax').text = str(botr[1])

        xml_str = ET.tostring(annotation)
        root = etree.fromstring(xml_str)
        xml_str = etree.tostring(root, pretty_print=True)
        extension = img_path.split('/')[-1].split('.')[-1]
        save_path = os.path.join(savedir, img_path.split('/')[-1].replace(extension, 'xml'))
        with open(save_path, 'wb') as temp_xml:
            temp_xml.write(xml_str)

    @staticmethod
    def _date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    @staticmethod
    def get_most_recent_model(path):
        files = glob.glob(os.path.join(path, '*'))
        files.sort(reverse=False)
        return files[0].split(path)[-1]

    def select_model(self, user, version=None, model_id=None):
        db = Database()

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
            version = model_path.split('/')[-1].split('_')[0]
            model_id = model_path.split('_')[-1]
            self.model_path = model_path
            if update_db:
                self.select_model(user=user, version=version, model_id=model_id)
        else:
            self.get_model_info(user)
            model_path = os.path.join(config.DATA_PATH, user, 'models', f'{self.version}_{self.model_id}.h5')
            self.model_path = model_path

        model = CustomObjectDetection()
        model.setModelTypeAsYOLOv3()
        model.setModelPath(model_path)
        model.setJsonPath(os.path.join(
            config.DATA_PATH,
            user,
            model_path.replace('models', 'models/json').replace('.h5', '.json')
        ))

        model.loadModel()

        return model

    def get_model_info(self, user, model=None):
        self.user = user
        if model:
            self.version = model.split('_')[0]
            self.model_id = model.split('_')[1]
        else:
            db = Database()
            models_df = db.read_db('models')
            models_df.where(cond=models_df.usr == user, inplace=True)
            self.version = models_df.version.tolist()[0]
            self.model_id = models_df.id.tolist()[0]
        self.model_name = f'{self.version}_{self.model_id}'

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

    def version_model(self, user):
        self.version = datetime.now().strftime("%Y-%m-%d-%h-%M-%S")
        self.generate_model_id(user)
        self.select_model(user=user)

    def train_model(self, data_dir, user, objs_array, model=None, new_model=False):
        if new_model:
            model_path = ''
        else:
            self.load_model(user=user, model_path=model)
            model_path = self.model_path

        model_trainer = DetectionModelTrainer()
        model_trainer.setModelTypeAsYOLOv3()
        model_trainer.setDataDirectory(data_directory=data_dir)
        model_trainer.setTrainConfig(
            object_names_array=list(set(objs_array)),
            batch_size=4,
            num_experiments=200,
            train_from_pretrained_model=model_path
        )
        model_trainer.trainModel()

        if new_model:
            self.version_model(user=user)

        self.model = model_trainer
        return self.model

    def detect(self, user, pic_path, model=None):
        path = Path('/' + os.path.join(*pic_path.split('/')[:-1]))
        path.mkdir(parents=True, exist_ok=True)

        out_pic_path_list = pic_path.split('/')
        out_pic_path_list.insert(-2, 'output')
        out_pic_path = os.path.join(*out_pic_path_list)
        path = Path('/' + os.path.join(*out_pic_path.split('/')[:-1]))
        path.mkdir(parents=True, exist_ok=True)

        detector = self.load_model(user, model)
        detections = detector.detectObjectsFromImage(
            input_image=pic_path,
            output_image_path=out_pic_path
        )

        results = dict()
        objs = list()
        br = list()
        tl = list()
        for obj in detections:
            objs.append(obj['name'])
            tl.append(tuple(obj['box_points'][1::2]))
            br.append(tuple(obj['box_points'][::2]))

        annotations_path = '/' + os.path.join(*pic_path.split('/')[:-2], 'annotations')
        self.write_xml(
            pic_path,
            objs,
            tl,
            br,
            annotations_path
        )
        return results, '', objs
