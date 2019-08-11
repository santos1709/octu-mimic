import json
import os
from contextlib import contextmanager

import requests
from flask import Flask, request
from flask import appcontext_pushed, g
from flask_jsonpify import jsonpify
from flask_restful import Resource, Api
from uuid import uuid4

from data_scanner import DataScanner
from db.database import Database
from model import Model

MAX_COUNT = 10


class DataSource(DataScanner):
    def __init__(self):
        super().__init__()

    def get_from_json(self, requester):
        got_json = request.json
        if type(got_json) == list:
            got_json = request.json[0]

        if requester == 'GetData':
            self.user = got_json['user']
            self.device = got_json['device']
            self.key = got_json['key']
            self.value = got_json['value']
            self.partial_token = got_json['token'].split('-')[-1]
            self.token = got_json['token']
            self.timestamp = got_json['timestamp']

        elif requester == 'SelectModel':
            self.model_name = got_json['model_name']
            self.model_version = got_json['model_version']

        elif requester == 'GenerateToken':
            self.user = got_json['user']
            self.device = got_json['device']

        elif requester == 'Train':
            self.user = got_json['user']
            self.device = got_json['device']
            self.token = got_json['token']
            self.timestamp = got_json['timestamp']

        self.update_path()
        self.update_full_path()


class GenerateToken(Resource):
    def put(self):
        data_source = g.data_source
        db = g.db

        data_source.get_from_json(requester=self.__class__.__name__)
        full_token = str(uuid4())
        token = full_token.split('-')[-1]
        table = f'{data_source.user}.{data_source.device}'

        # db.insert(table, values=[token, 0], columns=['token', 'count'])
        db.update_token(table, full_token)
        response = {'generated_token': full_token}
        return jsonpify(response)


class Train(Resource):
    def put(self):
        data_source = g.data_source
        model = g.model

        data_source.get_from_json(requester=self.__class__.__name__)
        model.train_model(data_source)
        response = {'Training info': {'model': model.model_name,
                                      'version': model.version,
                                      'train data size': model.train_data_size,
                                      'train status': 'successfully'}
                    }
        return jsonpify(response)


class GetData(Resource):
    def post(self):
        data_source = g.data_source
        db = g.db
        model = g.model
        data_source.get_from_json(requester=self.__class__.__name__)

        # TODO: get_from_db create table/first element
        count = db.select('count', f'{data_source.user}.{data_source.device}', 'token', data_source.token)
        if not count['data']:
            db.copy_to_db(f'{data_source.token}, 0', f'{data_source.user}.{data_source.device}')
            count['data'][0] = [0]

        count = int(count['data'][0][0]) + 1
        if count > MAX_COUNT:
            json_data = {"user": f'{data_source.user}', "device": f'{data_source.device}'}
            res = requests.put("http://127.0.0.1:8880/token/generate",
                               json=json_data)
            data_source.token = json.loads(res.text)['generated_token']
            count = 0

        if len(data_source.get_most_recents()) >= model.train_data_size:
            json_data = request.json
            requests.put("http://127.0.0.1:8880/model/train",
                         json=json_data)

        table = f'{data_source.user}.{data_source.device}'
        db.update(table, 'count', count, 'token', data_source.token)

        with open(f'{data_source.data_full_path}', 'a+') as file:
            file.write(data_source.value)
            file.write(',')


class SelectModel(Resource):
    def post(self):
        data_source = g.data_source
        model = g.model

        data_source.get_from_json(requester=self.__class__.__name__)
        model.name = data_source.model_name
        model.version = data_source.model_version
        model.update_model()

        response = {'new_model': {'model_name': model.name,
                                  'model_version': model.version
                                  }
                    }
        return jsonpify(response)


class ListModels(Resource):
    def get(self, path='models'):
        path = path.replace('_', '/')
        files = os.listdir(f'{path}/')
        files.sort(reverse=True)
        files_dict = {}
        for idx, file in enumerate(files):
            files_dict[f'model_{idx}'] = file

        return jsonpify(files_dict)


class Verify(Resource):
    def get(self, data):
        pass


class Alert(Resource):
    def get(self):
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
    api.add_resource(GetData, '/data/send')
    api.add_resource(Verify, '/data/verify/<string:path>')
    api.add_resource(Alert, '/data/alert')
    api.add_resource(Train, '/model/train')
    api.add_resource(SelectModel, '/model/select')
    api.add_resource(ListModels, '/model/list/<string:path>')
    api.add_resource(GenerateToken, '/token/generate')

    return app


if __name__ == '__main__':
    app = create_app()
    with objects_set(app, DataSource(), Database(), Model()):
        app.run(host='0.0.0.0', port='8880')
    # app.run(host='0.0.0.0', port='8080')
