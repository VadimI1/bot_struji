import psycopg2
from config import *


class bd_connect:
    def __init__(self, host, user, password, db_name):
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def setup(self):
        [self.sql_execute(TABLE[i]) for i in range(2)]

    def sql_execute(self, sql):
        return self.cursor.execute(sql)

    def sql_execute_get(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def bd_close(self):
        self.cursor.close()
        self.connection.close()