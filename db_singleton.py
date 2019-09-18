
import sqlite3

class DBSingleton:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = None
        self.cursor = None

    def get_instance(self):
        if self.db_conn is None:
            self.db_conn = sqlite3.connect(self.database_path)
            self.cursor = self.db_conn.cursor()
        return (self.db_conn, self.cursor)