import config


class DataScanner:
    def __init__(self):
        self.timestamp = ''
        self.user = ''
        self.device_name = ''
        self.data_path = ''
        self.uid = ''
        self.pic = ''
        self.model_version = ''
        self.model_id = ''
        self.last_untrained = ''
        self.new_model = ''
        self.operator = ''
        self.objs_array = []
        self.got_json = None

    def get_from_json(self, request, requester):
        got_json = request.json
        if type(got_json) == list:
            got_json = request.json[0]

        elif requester == 'SelectModel':
            self.user = got_json['user']
            self.model_version = got_json['model_version']
            self.model_id = got_json['model_id']

        elif requester == 'ListModels':
            self.user = got_json['user']

        elif requester == 'Evaluate':
            self.user = got_json['user']
            self.pic = got_json['picture']
            self.device_name = got_json['device_name']
            self.new_model = got_json.get('new_model')
            self.operator = got_json['operator']

        elif requester == 'Train':
            self.user = got_json['user']
            self.device_name = got_json['device_name']
            self.last_untrained = got_json['last_untrained']
            self.new_model = got_json['new_model']
            self.objs_array = got_json['objs']

        self.got_json = got_json
