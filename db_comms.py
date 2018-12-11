from flask import jsonify
import sqlite3

class Purchase:

    def __init__(self, item, price, category, date, note=None):
        self.item = item
        self.price = price
        self.category = category
        self.date = date
        self.note = note

class DBCommms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = sqlite3.connect(database_path)
        self.cursor = self.db_conn.cursor()

    def update_purchase(self, purchase_id, item, price, category, date, note):
        print("update_purchase()")
        print((purchase_id, item, price, category, date, note))

        self.cursor.execute(
        """UPDATE spending SET item = '{0}', price = {1}, category = '{2}', date = '{3}', note = '{4}'
        WHERE spending.purchase_id = {5}""".format(item,
        price, category, date, note, purchase_id))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated purchase!'})

    def delete_purchase(self, purchase_id):
        print("delete_purchase(): ")
        print(purchase_id)

        self.cursor.execute("DELETE FROM spending WHERE spending.purchase_id = {0};".format(int(purchase_id)))
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted purchase!'})


    def add_purchase(self, item, price, category, date, note):
        print("add_purchase()")
        print((item, price, category, date, note))

        # add purchase
        if note == "--":
            self.cursor.execute(
            """INSERT INTO spending (item, price, category, date, note)
            VALUES ('{0}', '{1}', '{2}', '{3}', NULL)""".format(item,
            price, category, date, note))
        else:
            self.cursor.execute(
            """INSERT INTO spending (item, price, category, date, note)
            VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(item,
            price, category, date, note))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added purchase!'})

    def get_purchases(self, month=None,year=None,category="ALL"):
        print("DBCommms : get_purchases({},{},{})".format(month, year, category))

        if month is None:
            begin_date = "{0}-01-01 00:00:00".format(year)
            end_date = "{0}-12-31 00:00:00".format(year)
        else:
            begin_date = "{0}-{1}-01 00:00:00".format(year, month)
            end_date = "{0}-{1}-31 00:00:00".format(year, month)

        if category == "ALL":
            self.cursor.execute("SELECT * FROM spending where spending.date >= '{0}' and spending.date <= '{1}'".format(begin_date, end_date))
        else:
            self.cursor.execute("SELECT * FROM spending where spending.date >= '{0}' and spending.date <= '{1}' and spending.category = '{2}'".format(begin_date, end_date, category))

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

        # send data
        return jsonify(data)

    def get_spending_report(self,month, year):
        print("get_spending_report()")
        print((month, year))

        # query
        begin_date = "{0}-{1}-01 00:00:00".format(year, month)
        end_date = "{0}-{1}-31 00:00:00".format(year, month)

        # get list of categories
        categories = {}
        self.cursor.execute("SELECT distinct(spending.category) from spending")
        for category in self.cursor:
            print("->: ", category[0])
            categories[category[0]] = 0.0

        # get month and year purchase data
        self.cursor.execute("SELECT spending.price, spending.category FROM spending where spending.date >= '{0}' and spending.date <= '{1}'".format(begin_date, end_date))

        # aggregate
        for price, category in self.cursor:
            categories[category] += float(price)

        # send data
        return jsonify(categories)

    def get_budget(self):
        print("get_budget()")

        # query
        self.cursor.execute("SELECT * FROM budget")

        # get list of categories
        data = []
        for category, amount, amount_frequency, category_id in self.cursor:
            contents = {}
            contents["category"] = category
            contents["amount"] = amount
            contents["amount_frequency"] = amount_frequency
            contents["category_id"] = category_id
            data.append(contents)

        # send data
        return jsonify(data)


    def __exit__(self):
        print("in __exit__")
