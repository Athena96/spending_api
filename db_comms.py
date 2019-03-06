from flask import jsonify
from models import Purchase
from models import Budget

import sqlite3

class DBCommms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = sqlite3.connect(database_path)
        self.cursor = self.db_conn.cursor()

    # Purchase Methods

    # add, update, delete
    def add_purchase(self, item, price, category, date, note):
        print("     " + self.__class__.__name__)
        print("     " + "add_purchase({}, {}, {}, {}, {})".format(item, price, category, date, note))

        # add purchase
        note = "NULL" if (note == "--" or note == "NULL" or note == None) else "'{0}'".format(note)

        q = """INSERT INTO spending (item, price, category, date, note) VALUES ('{0}', {1}, '{2}', '{3}', {4})""".format(item,
            price, category, date, note)
        print(q)
        self.cursor.execute(q)

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added purchase!'})

    def update_purchase(self, purchase_id, item, price, category, date, note):
        print("     " + self.__class__.__name__)
        print("     " + "update_purchase({}, {}, {}, {}, {}, {})".format(purchase_id, item, price, category, date, note))

        note = "NULL" if (note == "--" or note == "NULL" or note == None) else "'{0}'".format(note)
        self.cursor.execute("""UPDATE spending SET item = '{0}', price = {1}, category = '{2}', date = '{3}', note = {4} WHERE spending.purchase_id = {5}""".format(item,
        price, category, date, note, purchase_id))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated purchase!'})

    def delete_purchase(self, purchase_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_purchase({})", purchase_id)

        self.cursor.execute("DELETE FROM spending WHERE spending.purchase_id = {0};".format(int(purchase_id)))
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted purchase!'})

    # fetch
    def get_list_purchases(self, month=None, year=None, category="ALL"):
        print("     " + self.__class__.__name__)
        print("     " + "get_list_purchases({},{},{})".format(month, year, category))
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
        print("     " + q)

        self.cursor.execute(q)

        data = []
        for purchase_id, item, price, category, date, note in self.cursor:
            purchase = Purchase(item, price, category, date, note, purchase_id)
            data.append(purchase)

        # send data
        return data

    def get_purchase(self, purchase_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_purchase({})".format(purchase_id))
        if purchase_id is None:
            return None

        self.cursor.execute("SELECT * FROM spending where spending.purchase_id = {}".format(purchase_id))

        res = None
        for purchase_id, item, price, category, date, note in  self.cursor:
            res = Purchase(item, price, category, date, note, purchase_id)

        # send data
        return res

    def get_purchases(self, month=None, year=None, category="ALL"):
        print("     " + self.__class__.__name__)
        print("     " + "get_purchases({},{},{})".format(month, year, category))

        purchases = self.get_list_purchases(month, year, category)

        data = []
        for purchase in purchases:
            contents = {}
            contents["purchase_id"] = purchase.purchase_id
            contents["item"] = purchase.item
            contents["price"] = purchase.price
            contents["category"] = purchase.category
            contents["date"] = purchase.date
            contents["note"] = purchase.note
            data.append(contents)

        # send data
        return jsonify(data)


    # Budget Methods

    # add, update, delete
    def add_budget_category(self, category, amount, amount_frequency):
        print("     " + self.__class__.__name__)
        print("     " + "add_budget_category({}, {}, {}, )", category, amount, amount_frequency)

        # add budget category
        self.cursor.execute(
            """INSERT INTO budget (category, amount, amount_frequency) VALUES ('{0}', {1}, '{2}')""".format(category, amount, amount_frequency))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added budget category!'})

    def update_budget_category(self, category_id, category, amount, amount_frequency):
        print("     " + self.__class__.__name__)
        print("     " + "update_budget_category({}, {}, {}, {})", category_id, category, amount, amount_frequency)

        self.cursor.execute(
        """UPDATE budget SET category = '{0}', amount = {1}, amount_frequency = '{2}' WHERE budget.category_id = {3}""".format(category,
        amount, amount_frequency, category_id))

        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated budget category!'})

    def delete_budget_category(self, category_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_budget_category({})", category_id)

        # TODO is int() necessary?
        self.cursor.execute("DELETE FROM budget WHERE budget.category_id = {0};".format(int(category_id)))
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted budget category!'})

    # fetch
    def get_list_budgets(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_list_budgets()")

        # query
        self.cursor.execute("SELECT * FROM budget")

        # get list of categories
        data = []
        for category, amount, amount_frequency, category_id in self.cursor:
            budget = Budget(category, amount, amount_frequency, category_id)
            data.append(budget)

        # send data
        return data

    def get_budget(self, budget_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_a_budget({})".format(budget_id))
        if budget_id is None:
            return None

        self.cursor.execute("SELECT * FROM budget where budget.category_id = {}".format(budget_id))

        res = None
        for category, amount, amount_frequency, category_id in self.cursor:
            res = (category, amount, amount_frequency, category_id)

        # send data
        return res

    def get_budgets(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_budget()")

        budgets = self.get_list_budgets()

        # get list of categories
        data = []
        for budget in budgets:
            contents = {}
            contents["category"] = budget.category
            contents["amount"] = budget.amount
            contents["amount_frequency"] = budget.amount_frequency
            contents["category_id"] = budget.budget_id
            data.append(contents)

        # send data
        return jsonify(data)

    def __exit__(self):
        print("in __exit__")
