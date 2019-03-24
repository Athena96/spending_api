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
    def add_purchase(self, purchase):
        print("     " + self.__class__.__name__)
        print("     " + "add_purchase({})".format(purchase))

        # add purchase
        sql_note = "NULL" if (purchase.note == None) else "'{0}'".format(purchase.note)

        cmd = """INSERT INTO spending (item, price, category, date, note) VALUES ('{0}', {1}, '{2}', '{3}', {4})""".format(purchase.item,
            purchase.price, purchase.category, purchase.date, sql_note)
        print(cmd)
        self.cursor.execute(cmd)

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added purchase!'})

    def update_purchase(self, purchase):
        print("     " + self.__class__.__name__)
        print("     " + "update_purchase({})".format(purchase))

        sql_note = "NULL" if (purchase.note == None) else "'{0}'".format(purchase.note)

        cmd = """UPDATE spending SET item = '{0}', price = {1}, category = '{2}', date = '{3}', note = {4} WHERE spending.purchase_id = {5}""".format(purchase.item,
        purchase.price, purchase.category, purchase.date, sql_note, purchase.purchase_id)
        print(cmd)
        self.cursor.execute(cmd)

        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated purchase!'})

    def delete_purchase(self, purchase_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_purchase({})", purchase_id)

        self.cursor.execute("DELETE FROM spending WHERE spending.purchase_id = {0};".format(int(purchase_id)))
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted purchase!'})

    # fetch
    def get_purchases(self, month=None, year=None, category="ALL"):
        print("     " + self.__class__.__name__)
        print("     " + "get_purchases({},{},{})".format(month, year, category))
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


    # Budget Methods

    # add, update, delete
    def add_budget_category(self, budget):
        print("     " + self.__class__.__name__)
        print("     " + "add_budget_category({})", budget)

        # add budget category
        cmd = """INSERT INTO budget (category, amount, amount_frequency) VALUES ('{0}', {1}, '{2}')""".format(budget.category, budget.amount, budget.amount_frequency)
        print(cmd)
        self.cursor.execute(cmd)

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added budget category!'})

    def update_budget_category(self, budget):
        print("     " + self.__class__.__name__)
        print("     " + "update_budget_category({})", budget)

        cmd = """UPDATE budget SET category = '{0}', amount = {1}, amount_frequency = '{2}' WHERE budget.category_id = {3}""".format(budget.category,
        budget.amount, budget.amount_frequency, budget.budget_id)
        print(cmd)
        self.cursor.execute(cmd)

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
    def get_budgets(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_budgets()")

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
            res = Budget(category, amount, amount_frequency, category_id)

        # send data
        return res


    def __exit__(self):
        print("in __exit__")
