from io import StringIO

import pandas as pd
import psycopg2

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

    def update(self, table, column, value, where_col, where_val, *args):
        conn = self.conn

        def break_list(lst):
            for idx, el in enumerate(lst):
                yield (el, None) if idx % 2 == 0 else (None, f"'{el}'")

        if len(args) == 0:
            args = ''
        else:
            cols = [even[0] for even in break_list(args) if even[0]]
            vals = [odd[1] for odd in break_list(args) if odd[1]]
            args = list(zip(cols, vals))
            args = 'AND ' + ' AND '.join(list(map(lambda x: ' = '.join(x), args)))

        query = f""" UPDATE {table}
                     SET {column} = '{value}'
                     WHERE {where_col} = '{where_val}' 
                     {args} """

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

    def persist_on_db(self, df, table_name, if_exists='append'):
        df.to_sql(table_name, self.engine , index=False, if_exists=if_exists)

    def read_db(self, table_name):
        return pd.read_sql_table(table_name, self.engine)
