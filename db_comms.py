import sqlite3
from flask import jsonify
from models import Transaction
from models import Budget
from models import SpecialBudget

class DBCommms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = sqlite3.connect(database_path)
        self.cursor = self.db_conn.cursor()

    # Transaction Methods

    def add_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "add_transaction({})".format(transaction))

        sql_note = "NULL" if (transaction.description == None) else "'{0}'".format(transaction.description)

        cmd = """INSERT INTO ledger (title, amount, category, date, description) VALUES ('{0}', {1}, '{2}', '{3}', {4})""".format(transaction.title,
            transaction.amount, transaction.category, transaction.date, sql_note)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly added transaction!'})

    def update_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "update_transaction({})".format(transaction))

        sql_note = "NULL" if (transaction.description == None) else "'{0}'".format(transaction.description)

        cmd = """UPDATE ledger SET title = '{0}', amount = {1}, category = '{2}', date = '{3}', description = {4} WHERE ledger.transaction_id = {5}""".format(transaction.title,
        transaction.amount, transaction.category, transaction.date, sql_note, transaction.transaction_id)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated transaction!'})

    def delete_transaction(self, transaction_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_transaction({})", transaction_id)

        # TODO is int() necessary?
        cmd = "DELETE FROM ledger WHERE ledger.transaction_id = {0};".format(int(transaction_id))
        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted transaction!'})

    def get_transactions(self, month=None, year=None, category="ALL"):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction({},{},{})".format(month, year, category))

        base_query = "select * from ledger"

        date_query = ""
        if month is None:
            date_query = "ledger.date like('{}%')".format(year)
        else:
            date_query = "ledger.date like('{}-{}-%')".format(year, month)

        category_query = ""
        if category != "ALL":
            category_query = "ledger.category = '{}'".format(category)

        cmd = base_query + " where " + date_query + (" and " if category != "ALL" else "") + category_query
        print(cmd)

        self.cursor.execute(cmd)

        data = []
        for transaction_id, title, amount, category, date, description in self.cursor:
            transaction = Transaction(title, amount, category, date, description, transaction_id)
            data.append(transaction)

        return data

    def get_transaction(self, transaction_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction({})".format(transaction_id))

        if transaction_id is None:
            return None

        cmd = "SELECT * FROM ledger where ledger.transaction_id = {}".format(transaction_id)
        self.cursor.execute(cmd)

        res = None
        for transaction_id, title, amount, category, date, description in self.cursor:
            res = Transaction(title, amount, category, date, description, transaction_id)

        return res

    # Budget Methods

    def add_budget(self, budget):
        print("     " + self.__class__.__name__)
        print("     " + "add_budget({})", budget)

        sql_description = "NULL" if (budget.description == None) else "'{0}'".format(budget.description)

        cmd = """INSERT INTO budget (category, amount, amount_frequency, description) VALUES ('{0}', {1}, '{2}', {3})""".format(budget.category, budget.amount, budget.amount_frequency, sql_description)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly added budget category!'})

    def update_budget(self, budget):
        print("     " + self.__class__.__name__)
        print("     " + "update_budget({})", budget)

        sql_description = "NULL" if (budget.description == None) else "'{0}'".format(budget.description)

        cmd = """UPDATE budget SET category = '{0}', amount = {1}, amount_frequency = '{2}', description = {3} WHERE budget.budget_id = {4}""".format(budget.category,
        budget.amount, budget.amount_frequency, sql_description, budget.budget_id)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated budget category!'})

    def delete_budget(self, budget_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_budget({})", budget_id)

        # TODO is int() necessary?
        cmd = "DELETE FROM budget WHERE budget.budget_id = {0};".format(int(budget_id))
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted budget category!'})

    def get_budgets(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_budgets()")

        cmd = "SELECT * FROM budget"
        self.cursor.execute(cmd)

        data = []
        for category, amount, amount_frequency, budget_id, description in self.cursor:
            if "special" in amount_frequency:
                budget = SpecialBudget(category=category, amount=amount, amount_frequency=amount_frequency, description=description, budget_id=budget_id)
            else:
                budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, description=description, budget_id=budget_id)
            data.append(budget)

        return data

    def get_budget(self, budget_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_budget({})".format(budget_id))

        if budget_id is None:
            return None

        cmd = "SELECT * FROM budget where budget.budget_id = {}".format(budget_id)
        self.cursor.execute(cmd)

        res = None
        for category, amount, amount_frequency, budget_id, description in self.cursor:
            if "special" in amount_frequency:
                res = SpecialBudget(category=category, amount=amount, amount_frequency=amount_frequency, description=description, budget_id=budget_id)
            else:
                res = Budget(category=category, amount=amount, amount_frequency=amount_frequency, description=description, budget_id=budget_id)
        return res

    def __exit__(self):
        print("in __exit__")
