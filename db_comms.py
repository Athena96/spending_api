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
        print(self.__class__.__name__)
        print("update_purchase({}, {}, {}, {}, {}, {})", purchase_id, item, price, category, date, note)

        note = "NULL" if (note == "--" or note == "NULL" or note == None) else "'{0}'".format(note)
        self.cursor.execute(
        """UPDATE spending SET item = '{0}', price = {1}, category = '{2}', date = '{3}', note = {4}
        WHERE spending.purchase_id = {5}""".format(item,
        price, category, date, note, purchase_id))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated purchase!'})

    def delete_purchase(self, purchase_id):
        print(self.__class__.__name__)
        print("delete_purchase({})", purchase_id)

        self.cursor.execute("DELETE FROM spending WHERE spending.purchase_id = {0};".format(int(purchase_id)))
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted purchase!'})


    def add_purchase(self, item, price, category, date, note):
        print(self.__class__.__name__)
        print("add_purchase({}, {}, {}, {}, {})", item, price, category, date, note)

        # add purchase
        note = "NULL" if (note == "--" or note == "NULL" or note == None) else "'{0}'".format(note)
        self.cursor.execute(
            """INSERT INTO spending (item, price, category, date, note)
            VALUES ('{0}', {1}, '{2}', '{3}', {4})""".format(item,
            price, category, date, note))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added purchase!'})

    def get_list_purchases(self, month=None, year=None, category="ALL"):
        base_query = "select * from spending"

        date_query = ""
        if month is None:
            date_query = "spending.date like('{}%')".format(year)
        else:
            date_query = "spending.date like('{}-{}-%')".format(year, month)

        category_query = ""
        if category != "ALL":
            category_query = "spending.category = '{}'".format(category)

        q = base_query + " where " + date_query + (" and " if category != "ALL" else "") + category_query
        print(q)

        self.cursor.execute(q)

        data = []
        for purchase_id, item, price, category, date, note in self.cursor:
            p = (purchase_id, item, price, category, date, note)
            data.append(p)

        # send data
        return data

    def get_list_budgets(self):
        print(self.__class__.__name__)
        print("get_list_budgets()")

        # query
        self.cursor.execute("SELECT * FROM budget")

        # get list of categories
        data = []
        for category, amount, amount_frequency, category_id in self.cursor:
            b = (category, amount, amount_frequency, category_id)
            data.append(b)

        # send data
        return data

    def get_purchases(self, month=None,year=None,category="ALL"):
        print(self.__class__.__name__)
        print("get_purchases({},{},{})".format(month, year, category))

        result = self.get_list_purchases(month, year, category)

        data = []
        for purchase_id, item, price, category, date, note in result:
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

    def get_spending_report(self, month, year):
        print(self.__class__.__name__)
        print("get_spending_report({}, {})".format(month, year))

        # query
        begin_date = "{0}-{1}-01 00:00:00".format(year, month)
        end_date = "{0}-{1}-31 23:59:59".format(year, month)

        # get list of categories
        categories = {}
        self.cursor.execute("SELECT distinct(spending.category) from spending")
        for category in self.cursor:
            categories[category[0]] = 0.0

        # get month and year purchase data
        self.cursor.execute("SELECT spending.price, spending.category FROM spending where spending.date >= '{0}' and spending.date <= '{1}'".format(begin_date, end_date))

        # aggregate
        for price, category in self.cursor:
            categories[category] += float(price)

        # send data
        return jsonify(categories)

    def get_budget(self):
        print(self.__class__.__name__)
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

    def add_budget_category(self, category, amount, amount_frequency):
        print(self.__class__.__name__)
        print("add_budget_category({}, {}, {}, )", category, amount, amount_frequency)

        # add budget category
        self.cursor.execute(
            """INSERT INTO budget (category, amount, amount_frequency)
            VALUES ('{0}', {1}, '{2}')""".format(category, amount, amount_frequency))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added budget category!'})

    def update_budget_category(self, category_id, category, amount, amount_frequency):
        print(self.__class__.__name__)
        print("update_budget_category({}, {}, {}, {})", category_id, category, amount, amount_frequency)

        self.cursor.execute(
        """UPDATE budget SET category = '{0}', amount = {1}, amount_frequency = '{2}'
        WHERE budget.category_id = {3}""".format(category,
        amount, amount_frequency, category_id))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated budget category!'})

    def delete_budget_category(self, category_id):
        print(self.__class__.__name__)
        print("delete_budget_category({})", category_id)

        # TODO is int() necessary?
        self.cursor.execute("DELETE FROM budget WHERE budget.category_id = {0};".format(int(category_id)))
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted budget category!'})

    def __exit__(self):
        print("in __exit__")
