from flask import Flask
from flask_restful import Resource, Api
from uuid import uuid4
from db.database import Database
from model import Model
import requests
import os
from flask import Flask, request
from flask_jsonpify import jsonpify
from flask_restful import Resource, Api
from io import StringIO

app = Flask(__name__)
api = Api(app)
MAX_COUNT = 10


class Data:
    def __init__(self):
        self.key = ''
        self.value = ''
        self.token = ''
        self.timestamp = ''
        self.model_name = ''
        self.model_version = ''
        self.user = ''
        self.device = ''

    def get_from_file(self, element, filtering=None):
        pass

    def get_from_json(self, requester):
        json = request.json
        if type(json) == list:
            json = request.json[0]

        if requester == 'GetData':
            self.user = json['user']
            self.device = json['device']
            self.key = json['key']
            self.value = json['value']
            self.token = json['token']
            self.timestamp = json['timestamp']

        elif requester == 'SelectModel':
            self.model_name = json['model_name']
            self.model_version = json['model_version']

        elif requester == 'GenerateToken':
            self.user = json['user']
            self.device = json['device']

        elif requester == 'Train':
            self.token = json['token']
            self.timestamp = json['timestamp']


class GenerateToken(Resource):
    def post(self):
        data_source.get_from_json(requester=self.__class__.__name__)

        token = str(uuid4()).replace('-', '')
        table = f'{data_source.user}.{data_source.device}'
        db.update(table, token=token)
        db.update(table, token=token, count=0)

        response = {'generated_token': token}
        return jsonpify(response)


class Train(Resource):
    def put(self):
        data_source.get_from_json(requester=self.__class__.__name__)

        # model.train_model(data_source.token, data_source.timestamp)
        pass


class SendData(Resource):
    def post(self):
        data_source.get_from_json(requester=self.__class__.__name__)

        # import pdb; pdb.set_trace()
        # TODO: get_from_db create table/first element
        count = db.get_from_db('count', f'{data_source.user}.{data_source.device}', data_source.token)
        if not count['data']:
            db.copy_to_db(f'{data_source.token}, 0', f'{data_source.user}.{data_source.device}')
            count['data'][0] = [0]

        count = int(count['data'][0][0]) + 1
        if count > MAX_COUNT:
            json_data = {"user": f'{data_source.user}', "device": f'{data_source.device}'}
            requests.put("http://127.0.0.1:8080/token/generate",
                         json=json_data)

            json_data = {"token": f'{data_source.token}', "timestamp": f'{data_source.timestamp}'}
            requests.put("http://127.0.0.1:8080/model/train",
                         json=json_data)

        table = f'{data_source.user}.{data_source.device}'
        db.update(table, token=data_source.token, count=count)
        with open(f'data/{data_source.timestamp}_{data_source.key}_{data_source.token}.csv', 'a+') as file:
            file.write(data_source.value)
            file.write(',')


class SelectModel(Resource):
    def post(self):
        data_source.get_from_json(requester=self.__class__.__name__)
        # model.name = data_source.model_name
        # model.version = data_source.model_version
        # model.update_model()

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
    def get(self):
        pass


class Alert(Resource):
    def get(self):
        pass


api.add_resource(SendData, '/data/send')
api.add_resource(Verify, '/data/verify')
api.add_resource(Alert, '/data/alert')
api.add_resource(Train, '/model/train')
api.add_resource(SelectModel, '/model/select')
api.add_resource(ListModels, '/model/list/<string:path>')
api.add_resource(GenerateToken, '/token/generate')

if __name__ == '__main__':
    # model = Model()
    db = Database()
    data_source = Data()
    app.run(host='0.0.0.0', port='8080')
