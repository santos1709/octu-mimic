from sqlalchemy import create_engine
import config

DB_NAME = config.DB['DB_NAME']
USERNAME = config.DB['USERNAME']
HOST = config.DB['HOST']
PASSWORD = config.DB['PASSWORD']
PORT = config.DB['PORT']
TIMEOUT_VALUE = 60 * 60 * 1000


class DbRepository:
    @staticmethod
    def get_engine():
        return create_engine(
            'postgresql://{}:{}@{}:{}/{}'.format(USERNAME, PASSWORD, HOST, PORT, DB_NAME),
            pool_pre_ping=True)
