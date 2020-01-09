import json
import os
from contextlib import contextmanager
from uuid import uuid4

import requests
from flask import Flask, request
from flask import appcontext_pushed, g
from flask_jsonpify import jsonpify
from flask_restful import Resource, Api
from keras import backend as K

from data_scanner import DataScanner
from db.database import Database
from model import Model
import config


class DataSource(DataScanner):
    def __init__(self):
        self.got_json = None
        super().__init__()

    def get_from_json(self, requester):
        got_json = request.json
        if type(got_json) == list:
            got_json = request.json[0]

        elif requester == 'SelectModel':
            self.model_name = got_json['model_name']
            self.model_version = got_json['model_version']

        elif requester == 'Evaluate':
            self.user = got_json['user']
            self.pic = got_json['picture']
            self.device_name = got_json['device_name']
            self.operator = got_json['operator']

        elif requester == 'Train':
            self.user = got_json['user']
            self.device_name = got_json['device_name']
            self.last_untrained = got_json['last_untrained']
            self.new_model = got_json['new_model']

        self.got_json = got_json


class Train(Resource):
    def put(self):
        data_source = g.data_source
        data_source.get_from_json(requester=self.__class__.__name__)

        model = g.model
        if data_source.new_model != "":
            user = data_source.user
        else:
            user = None
        model.train_model(
            data_dir=os.path.join(config.UNTRAINED_IMAGES_PATH, data_source.last_untrained),
            user=user
        )

        response = {
            'Training info': {
                'model': model.model_name,
                'version': model.version,
                'train data size': model.train_data_size,
                'train status': 'successfully'
            }
        }
        return jsonpify(response)


class SelectModel(Resource):
    def post(self):
        data_source = g.data_source
        data_source.get_from_json(requester=self.__class__.__name__)

        model = g.model
        model.select_model(user=data_source.user, name=data_source.model_name, version=data_source.model_version)

        response = {
            'new_model': {
                'model_name': model.model_name,
                'model_version': model.version
            }
        }
        return jsonpify(response)


class ListModels(Resource):
    def get(self):
        path = config.MODELS_PATH
        path = path.replace('_', '/')
        files = os.listdir(f'{path}/')
        files.sort(reverse=True)
        files_dict = {}
        for idx, file in enumerate(files):
            files_dict[f'model_{idx}'] = file

        return jsonpify(files_dict)


class Evaluate(Resource):
    def get(self):
        data_source = g.data_source
        data_source.get_from_json(requester=self.__class__.__name__)

        model = g.model
        file_path = os.path.join(config.PICS_PATH, data_source.device_name, data_source.pic)

        res, last_untrained = model.detect(file_path)

        json_data = {
            'user': data_source.user,
            'device': data_source.device_name,
            'operator': data_source.operator,
            'results': res,
            'last_untrained': last_untrained
        }
        requests.put("http://127.0.0.1:8880/validate", json=json_data)
        requests.put("http://127.0.0.1:8880/train", json=json_data)

        return jsonpify(res)


class Validate(Resource):
    def get(self):
        # TODO: Fill up the google sheet with all the relevant information
        pass


@contextmanager
def objects_set(app, data_source, db, model):
    """ This allows to set (simulate) session objects with arbitrary ones """

    def handler(sender, **kwargs):
        g.data_source = data_source
        g.db = db
        g.model = model

    with appcontext_pushed.connected_to(handler, app):
        yield


def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Evaluate, '/data/evaluate')
    api.add_resource(Validate, '/data/validate')
    api.add_resource(Train, '/model/train')
    api.add_resource(SelectModel, '/model/select')
    api.add_resource(ListModels, '/model/list')

    return app


if __name__ == '__main__':
    app = create_app()
    with objects_set(app, DataSource(), Database(), Model()):
        app.run(host='0.0.0.0', port='8880')
