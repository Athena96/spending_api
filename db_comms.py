import sqlite3
from flask import jsonify
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from models import Transaction
from models import Budget
from models import Period

class DBCommms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = None
        self.cursor = None

    def get_instance(self):
        if self.db_conn is None:
            self.db_conn = sqlite3.connect(self.database_path)
            self.cursor = self.db_conn.cursor()
        return (self.db_conn, self.cursor)

    # Transaction Methods

    def add_transaction(self, transaction):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "add_transaction({})".format(transaction))

        sql_note = "NULL" if (transaction.description == None) else "'{0}'".format(transaction.description)

        cmd = """INSERT INTO ledger (title, amount, category, date, description) VALUES ('{0}', {1}, '{2}', '{3}', {4})""".format(transaction.title,
            transaction.amount, ",".join(transaction.get_categories()), transaction.date, sql_note)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()
        self.db_conn.close()

        return jsonify({'result': 'successfuly added transaction!'})

    def update_transaction(self, transaction):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "update_transaction({})".format(transaction))

        sql_note = "NULL" if (transaction.description == None) else "'{0}'".format(transaction.description)

        cmd = """UPDATE ledger SET title = '{0}', amount = {1}, category = '{2}', date = '{3}', description = {4} WHERE ledger.transaction_id = {5}""".format(transaction.title,
        transaction.amount, ",".join(transaction.get_categories()), transaction.date, sql_note, transaction.transaction_id)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated transaction!'})

    def delete_transaction(self, transaction_id):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "delete_transaction({})", transaction_id)

        cmd = "DELETE FROM ledger WHERE ledger.transaction_id = {0};".format(int(transaction_id))
        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted transaction!'})

    def get_transactions(self, month=None, year=None, category="ALL"):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "get_transaction(month:{},year:{},category:{})".format(month, year, category))

        base_query = "select * from ledger"

        date_query = ""
        if month is None:
            date_query = "ledger.date like('{}%')".format(year)
        else:
            date_query = "ledger.date like('{}-{}-%')".format(year, month)

        category_query = ""
        if category != "ALL":
            category_query = "ledger.category like '%{}%'".format(category)

        cmd = base_query + " where " + date_query + (" and " if category != "ALL" else "") + category_query
        print(cmd)

        self.cursor.execute(cmd)

        data = []
        for transaction_id, title, amount, category, date, description in self.cursor:
            description = None if description == "null" else description
            transaction = Transaction(title, amount, category, date, description, transaction_id)
            data.append(transaction)

        return data

    def get_period_transactions(self, start_date, end_date, category=None):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)

        base_query = "select * from ledger"

        date_query = "ledger.date >= '{}-{}-{} 00:00:00' and ledger.date <= '{}-{}-{} 23:59:59'".format(start_date.year,
            '{:02d}'.format(start_date.month), '{:02d}'.format(start_date.day), end_date.year,
            '{:02d}'.format(end_date.month), '{:02d}'.format(end_date.day))

        category_query = ""
        if category is not None:
            category_query = "ledger.category = '{}'".format(category.name)

        cmd = base_query + " where " + date_query + (" and " if category is not None else "") + category_query
        print(cmd)

        self.cursor.execute(cmd)

        data = []
        for transaction_id, title, amount, category, date, description in self.cursor:
            description = None if description == "null" else description
            transaction = Transaction(title, amount, category, date, description, transaction_id)
            data.append(transaction)

        return data

    def get_transaction(self, transaction_id):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "get_transaction({})".format(transaction_id))

        if transaction_id is None:
            return None

        cmd = "SELECT * FROM ledger where ledger.transaction_id = {}".format(transaction_id)
        self.cursor.execute(cmd)

        res = None
        for transaction_id, title, amount, category, date, description in self.cursor:
            description = None if description == "null" else description
            res = Transaction(title, amount, category, date, description, transaction_id)

        return res

    def get_min_max_transaction_dates(self):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "get_min_max_transaction_dates()")

        cmd = """select min(ledger.date)
            from ledger"""
        self.cursor.execute(cmd)
        min_date = self.cursor.fetchone()[0]
        min_month = int(min_date[5:7])
        min_year = int(min_date[0:4])

        cmd = """select max(ledger.date)
            from ledger"""
        self.cursor.execute(cmd)
        max_date = self.cursor.fetchone()[0]
        max_month = int(max_date[5:7])
        max_year = int(max_date[0:4])

        return (min_year, months(min_month, min_year, max_month, max_year))

    # Budget Methods

    def add_budget(self, budget):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "add_budget({})", budget)

        sql_description = "NULL" if (budget.description == None) else "'{0}'".format(budget.description)

        cmd = """INSERT INTO budget (category, amount, amount_frequency, description, start_date, end_date) VALUES ('{0}', {1}, '{2}', {3}, '{4}', '{5}')""".format(budget.category.name, budget.amount, budget.amount_frequency, sql_description, budget.start_date, budget.end_date)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly added budget category!'})

    def update_budget(self, budget):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "update_budget({})", budget)

        sql_description = "NULL" if (budget.description == None) else "'{0}'".format(budget.description)

        cmd = """UPDATE budget SET category = '{0}', amount = {1}, amount_frequency = '{2}', description = {3}, start_date = '{4}', end_date = '{5}' WHERE budget.category_id = {6}""".format(budget.category.name,
        budget.amount, budget.amount_frequency, sql_description, budget.start_date, budget.end_date, budget.budget_id)
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated budget category!'})

    def delete_budget(self, budget_id):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "delete_budget({})", budget_id)

        cmd = "DELETE FROM budget WHERE budget.category_id = {0};".format(int(budget_id))
        print(cmd)

        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted budget category!'})

    def get_budgets(self, date):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "get_budgets({})".format(date))

        cmd = """select * from budget where budget.start_date <= '{0}-{1}-{2} {3}:{4}:{5}' and budget.end_date >= '{0}-{1}-{2} {3}:{4}:{5}' """.format(date.year, '{:02d}'.format(date.month), '{:02d}'.format(date.day), '{:02d}'.format(date.hour), '{:02d}'.format(date.minute), '{:02d}'.format(date.second))
        self.cursor.execute(cmd)
        print(cmd)

        data = []
        for category, amount, amount_frequency, budget_id, description, start_date, end_date in self.cursor:
            description = None if description == "null" else description
            if "period" in amount_frequency:
                budget = Period(category=category, amount=amount, start_date=start_date, end_date=end_date, description=description, budget_id=budget_id)
            else:
                budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description, budget_id=budget_id)
            data.append(budget)

        return data

    def get_budget(self, budget_id):
        (self.db_conn, self.cursor) = self.get_instance()

        print("     " + self.__class__.__name__)
        print("     " + "get_budget({})".format(budget_id))

        if budget_id is None:
            return None

        cmd = "SELECT * FROM budget where budget.category_id = {}".format(budget_id)
        self.cursor.execute(cmd)

        res = None
        for category, amount, amount_frequency, budget_id, description, start_date, end_date in self.cursor:
            description = None if description == "null" else description
            if "period" in amount_frequency:
                res = Period(category=category, amount=amount, start_date=start_date, end_date=end_date, description=description, budget_id=budget_id)
            else:
                res = Budget(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description, budget_id=budget_id)
        return res

    def __exit__(self):
        print("in __exit__")

# helper
def months(start_month, start_year, end_month, end_year):
    print("Helper: months({},{},{},{})".format(start_month, start_year, end_month, end_year))

    start = datetime(start_year, start_month, 1)
    end = datetime(end_year, end_month, 1)
    return [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]
