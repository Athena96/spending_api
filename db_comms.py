
import sqlite3

class DBCommms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = sqlite3.connect(database_path)
        self.cursor = self.db_conn.cursor()

    def get_purchases(self, month=None,year=None,category=None):
        print("get_purchases ->>>>>>")

        begin_date = "{0}-01-01 00:00:00".format(year)
        end_date = "{0}-12-31 00:00:00".format(year)
        self.cursor.execute("SELECT * FROM spending where spending.date >= '{0}' and spending.date <= '{1}'".format(begin_date, end_date))
        data = []
        for purchase_id, item, price, category, date, note in self.cursor:
            contents = {}
            contents["purchase_id"] = purchase_id
            contents["item"] = item
            contents["price"] = price
            contents["category"] = category
            contents["date"] = date
            contents["note"] = note
            data.append(contents)

        return data



    def __exit__(self):
        print("in __exit__")
