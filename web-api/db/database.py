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

    def select(self, what, table, where_col=None, where_val=None):
        conn = self.conn
        conn.autocommit = True
        cur = conn.cursor()

        where_clause = "" if not where_col else f"WHERE {where_col} = '{where_val}'"
        try:
            cur.execute(f"SELECT {what} FROM {table} {where_clause}")
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

    def update_token(self, table, new_token):
        old_token = self.select('token', table)['data'][0][0]

        self.update(table, 'token', new_token, 'token', old_token)

    def update(self, table, column, value, where_col, where_val):
        conn = self.conn
        query = f""" UPDATE {table}
                     SET {column} = '{value}'
                     WHERE {where_col} = '{where_val}' """

        with conn.cursor() as c:
            c.execute(query)
            conn.commit()

    def insert(self, table, values, columns=None):
        conn = self.conn
        columns = "" if not columns else f"{str(columns).replace('[', '(').replace(']', ')')}"
        query = f""" INSERT INTO {table}
                     {str(columns).replace("'", "")} VALUES 
                     {str(values).replace('[', '(').replace(']', ')')} """

        with conn.cursor() as c:
            c.execute(query)
            conn.commit()
