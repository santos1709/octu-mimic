import os


class DataScanner:
    def __init__(self):
        self.key = ''
        self.value = ''
        self.token = ''
        self.timestamp = ''
        self.model_name = ''
        self.model_version = ''
        self.user = ''
        self.device = ''
        self.data_path = self._get_path()
        self.data_full_path = self._get_full_path()

    def _get_path(self):
        return f'data/{self.user}/{self.device}'

    def _get_full_path(self):
        return f'{self.data_path}/{self.timestamp}_{self.key}_{self.token}.csv'

    def iter_files(self):
        data_files = os.listdir(self.data_path)
        for file in data_files:
            file = os.path.abspath(file).split(os.getcwd())[1]
            self.key = file.split('_')[1]
            self.token = file.split('_')[-1].split('.')[0]
            self.timestamp = file.split('_')[0].split('/')[-1]
            self.user = file.split('/')[1]
            self.device = file.split('/')[2]
            yield file

    def get_most_recents(self, size=None):
        top_size = []
        if size is None:
            for file in self.iter_files():
                if len(self.token) < 13:
                    top_size.append(file)
                    continue
                return top_size
        else:
            for length, file in enumerate(self.iter_files()):
                if length <= size:
                    top_size.append(file)
                    continue
                return top_size
