import psycopg2
from io import StringIO

from db.db_repository import *


class Database:
    def __init__(self):
        db_repository = DbRepository()
        self.engine = db_repository.get_engine()
        self.default_table = ''
        self.last_table = self.default_table
        self.conn = psycopg2.connect(host=HOST, database=DB_NAME, user=USERNAME, port=PORT, password=PASSWORD)

    def get_from_db(self, element, table_name, token):
        conn = self.conn
        conn.autocommit = True
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT {element} FROM {table_name} WHERE token = '{token}'")
            fetchall = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            return {'columns': columns, 'data': fetchall}
        except Exception as e:
            fetchall = None
            status_message = str(e)

            return {'status': status_message, 'all': fetchall}

    def copy_to_db(self, data, table):
        conn = self.conn

        sio = StringIO()
        sio.write(data)
        sio.seek(0)

        with conn.cursor() as c:
            c.copy_from(sio, table, sep=',')
            conn.commit()

    def update(self, table, token, count=None):
        conn = self.conn
        to_set = 'count'
        param = count
        if count is None:
            to_set = 'token'
            param = token

        query = f""" UPDATE {table}
                     SET {to_set}= %s
                     WHERE token = {token} """

        with conn.cursor() as c:
            c.execute(query, param)
            conn.commit()
