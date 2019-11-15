import sqlite3


class DBComms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = None
        self.cursor = None

    def get_instance(self):
        self.db_conn = sqlite3.connect(self.database_path)
        self.cursor = self.db_conn.cursor()
        return (self.db_conn, self.cursor)

    def __exit__(self):
        print("in __exit__")
