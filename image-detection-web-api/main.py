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

from data_scanner import DataScanner as DataSource
from db.database import Database
from model import Model
import config


class Train(Resource):
    def post(self):
        data_source = g.data_source
        data_source.get_from_json(request=request, requester=self.__class__.__name__)

        model = g.model
        if data_source.new_model == "yes":
            new_model = True
        else:
            new_model = False
        model.train_model(
            objs_array=data_source.objs_array,
            data_dir=os.path.join(config.DATA_PATH, data_source.user, data_source.last_untrained),
            user=data_source.user,
            new_model=new_model
        )

        K.clear_session()
        response = {
            'Training info': {
                'model_name': model.model_name,
                'version': model.version,
                'train data size': model.train_data_size,
                'train status': 'successfully'
            }
        }
        return jsonpify(response)


class SelectModel(Resource):
    def post(self):
        data_source = g.data_source
        data_source.get_from_json(request=request, requester=self.__class__.__name__)

        model = g.model
        model.select_model(
            user=data_source.user,
            version=data_source.model_version,
            model_id=data_source.model_id
        )

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
    def post(self):
        data_source = g.data_source
        data_source.get_from_json(request=request, requester=self.__class__.__name__)

        model = g.model
        res, last_untrained, objs = model.detect(user=data_source.user, pic_path=data_source.pic)

        new_model = data_source.new_model
        if not new_model:
            new_model = 'no'

        json_data = {
            'user': data_source.user,
            'device_name': data_source.device_name,
            'operator': data_source.operator,
            'results': res,
            'new_model': new_model,
            'last_untrained': last_untrained,
            'objs': objs
        }
        K.clear_session()
        requests.get(f'{config.HOST_NAME}{config.VALIDATE_ROUTE}', json=json_data)
        requests.post(f'{config.HOST_NAME}{config.TRAIN_ROUTE}', json=json_data)

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
    api.add_resource(Evaluate, config.EVALUATE_ROUTE)
    api.add_resource(Validate, config.VALIDATE_ROUTE)
    api.add_resource(Train, config.TRAIN_ROUTE)
    api.add_resource(SelectModel, config.SELECT_ROUTE)
    api.add_resource(ListModels, config.LIST_ROUTE)

    return app


if __name__ == '__main__':
    app = create_app()
    with objects_set(app, DataSource(), Database(), Model()):
        app.run(host=config.HOST, port=config.PORT)
