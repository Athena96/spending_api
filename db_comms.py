import sqlite3
from flask import jsonify
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from models import Transaction
from models import Recurrence
from models import Period
from models import RecurrenceType

class DBCommms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = None
        self.cursor = None

    def get_instance(self):
        self.db_conn = sqlite3.connect(self.database_path)
        self.cursor = self.db_conn.cursor()
        return (self.db_conn, self.cursor)

    # Add Methods

    def add_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "add_transaction({})".format(transaction))
        (self.db_conn, self.cursor) = self.get_instance()

        sql_note = "NULL" if (transaction.description == None) else "'{0}'".format(transaction.description)

        cmd = """INSERT INTO ledger (title, amount, category, date, description) VALUES ('{0}', {1}, '{2}', '{3}', {4})""".format(transaction.title,
            transaction.amount, ",".join(transaction.get_categories()), transaction.date, sql_note)
        self.cursor.execute(cmd)
        self.db_conn.commit()
        self.db_conn.close()
        print(cmd)

        return jsonify({'result': 'successfuly added transaction!'})

    def add_recurrence(self, recurrence):
        print("     " + self.__class__.__name__)
        print("     " + "add_recurrence({})", recurrence)
        (self.db_conn, self.cursor) = self.get_instance()

        sql_description = "NULL" if (recurrence.description == None) else "'{0}'".format(recurrence.description)

        cmd = """INSERT INTO budget (category, amount, amount_frequency, description, start_date, end_date) VALUES ('{0}', {1}, '{2}', {3}, '{4}', '{5}')""".format(recurrence.category.name, recurrence.amount, recurrence.amount_frequency, sql_description, recurrence.start_date, recurrence.end_date)
        self.cursor.execute(cmd)
        self.db_conn.commit()
        self.db_conn.close()
        print(cmd)

        return jsonify({'result': 'successfuly added recurrence category!'})

    # Update Methods

    def update_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "update_transaction({})".format(transaction))
        (self.db_conn, self.cursor) = self.get_instance()

        sql_note = "NULL" if (transaction.description == None) else "'{0}'".format(transaction.description)

        cmd = """UPDATE ledger SET title = '{0}', amount = {1}, category = '{2}', date = '{3}', description = {4} WHERE ledger.transaction_id = {5}""".format(transaction.title,
        transaction.amount, ",".join(transaction.get_categories()), transaction.date, sql_note, transaction.transaction_id)
        self.cursor.execute(cmd)
        self.db_conn.commit()
        print(cmd)

        return jsonify({'result': 'successfuly updated transaction!'})

    def update_recurrence(self, recurrence):
        print("     " + self.__class__.__name__)
        print("     " + "update_recurrence({})", recurrence)
        (self.db_conn, self.cursor) = self.get_instance()

        sql_description = "NULL" if (recurrence.description == None) else "'{0}'".format(recurrence.description)

        cmd = """UPDATE budget SET category = '{0}', amount = {1}, amount_frequency = '{2}', description = {3}, start_date = '{4}', end_date = '{5}' WHERE budget.category_id = {6}""".format(recurrence.category.name,
                                                                                                                                                                                              recurrence.amount, recurrence.amount_frequency, sql_description, recurrence.start_date, recurrence.end_date, recurrence.recurrence_id)
        self.cursor.execute(cmd)
        self.db_conn.commit()
        print(cmd)

        return jsonify({'result': 'successfuly updated recurrence category!'})

    # Delete Methods

    def delete_transaction(self, transaction_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_transaction({})", transaction_id)
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = "DELETE FROM ledger WHERE ledger.transaction_id = {0};".format(int(transaction_id))
        self.cursor.execute(cmd)
        self.db_conn.commit()
        print(cmd)

        return jsonify({'result': 'successfuly deleted transaction!'})

    def delete_recurrence(self, recurrence_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_recurrence({})", recurrence_id)
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = "DELETE FROM budget WHERE budget.category_id = {0};".format(int(recurrence_id))
        self.cursor.execute(cmd)
        self.db_conn.commit()
        print(cmd)

        return jsonify({'result': 'successfuly deleted recurrence category!'})

    # Query Methods

    def get_transactions(self, year=None, month=None, category="ALL"):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction(month:{},year:{},category:{})".format(month, year, category))
        (self.db_conn, self.cursor) = self.get_instance()
        # todo update category so that you pass obj and not string (or change recurrence to not store category as Obj)

        base_query = "select * from ledger"
        if month is None:
            date_query = "ledger.date like('{}%')".format(year)
        else:
            date_query = "ledger.date like('{}-{}-%')".format(year, month)

        category_query = ""
        if category != "ALL":
            category_query = "ledger.category like '%{}%'".format(category)

        cmd = base_query + " where " + date_query + (" and " if category != "ALL" else "") + category_query
        self.cursor.execute(cmd)
        print(cmd)

        return self.extract_transactions(self.cursor)

    def get_transaction(self, transaction_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction({})".format(transaction_id))
        (self.db_conn, self.cursor) = self.get_instance()

        if transaction_id is None:
            return None

        cmd = "SELECT * FROM ledger where ledger.transaction_id = {}".format(transaction_id)
        self.cursor.execute(cmd)
        print(cmd)

        result = self.extract_transactions(self.cursor)
        return None if len(result) == 0 or len(result) > 1 else result[0]

    def get_transactions_between(self, start_date, end_date, category=None):
        print("     " + self.__class__.__name__)
        print("     " + "get_transactions_between()")
        (self.db_conn, self.cursor) = self.get_instance()

        base_query = "select * from ledger"

        date_query = "ledger.date >= '{}-{}-{} 00:00:00' and ledger.date <= '{}-{}-{} 23:59:59'".format(start_date.year,
            '{:02d}'.format(start_date.month), '{:02d}'.format(start_date.day), end_date.year,
            '{:02d}'.format(end_date.month), '{:02d}'.format(end_date.day))

        category_query = ""
        if category is not None:
            category_query = "ledger.category = '{}'".format(category.name)

        cmd = base_query + " where " + date_query + (" and " if category is not None else "") + category_query
        self.cursor.execute(cmd)
        print(cmd)

        return self.extract_transactions(self.cursor)

    def get_recurrences(self, date):
        print("     " + self.__class__.__name__)
        print("     " + "get_recurrences({})".format(date))
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = """select * from budget where budget.start_date <= '{0}-{1}-{2} {3}:{4}:{5}' and budget.end_date >= '{0}-{1}-{2} {3}:{4}:{5}' """.format(date.year, '{:02d}'.format(date.month), '{:02d}'.format(date.day), '{:02d}'.format(date.hour), '{:02d}'.format(date.minute), '{:02d}'.format(date.second))
        self.cursor.execute(cmd)
        print(cmd)

        return self.extract_recurrence(self.cursor)

    def get_recurrence(self, recurrence_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_recurrence({})".format(recurrence_id))
        (self.db_conn, self.cursor) = self.get_instance()

        if recurrence_id is None:
            return None

        cmd = "SELECT * FROM budget where budget.category_id = {}".format(recurrence_id)
        self.cursor.execute(cmd)
        print(cmd)

        result = self.extract_recurrence(self.cursor)
        return None if len(result) == 0 or len(result) > 1 else result[0]

    # Helper

    def get_spending(self, year, month):
        print("     " + self.__class__.__name__)
        print("     " + "get_spending()")

        year_transactions = self.get_transactions(year=year)

        if month is not None:
            # 3 filter month transactions
            month_transactions = [transaction for transaction in year_transactions if (transaction.date[5:7] == month)]

            # 4 calculate spent_in_year
            spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income) and int(transaction.date[5:7]) <= int(month)])
            spent_in_year_str = str(round(spent_in_year, 2))

            # 5 calculate spent_in_month
            spent_in_month = sum([transaction.amount for transaction in month_transactions if (not transaction.category[0].is_income)])
            spent_in_month_str = str(round(spent_in_month, 2))
        else:
            # 4 calculate spent_in_month
            spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income)])
            spent_in_year_str = str(round(spent_in_year, 2))

            # 5 calculate spent_in_month
            spent_in_month_str = "--"

        return (spent_in_year_str, spent_in_month_str)

    def get_income(self, year, month):
        print("     " + self.__class__.__name__)
        print("     " + "get_income()")
        if month is None:
            return ("--", "--")

        year_transactions = self.get_transactions(year=year)

        year_income = round(sum([transaction.amount for transaction in year_transactions if
                                 transaction.category[0].is_income and int(transaction.date[5:7]) <= int(month)]), 2)
        month_income = round(sum([transaction.amount for transaction in year_transactions if
                                  (transaction.category[0].is_income and (transaction.date[5:7] == month))]), 2)
        return (year_income, month_income)

    def extract_transactions(self, cursor):
        print("     " + self.__class__.__name__)
        print("     " + "extract_transactions()")
        data = []
        for transaction_id, title, amount, category, date, description in cursor:
            description = None if description == "null" else description
            transaction = Transaction(title, amount, category, date, description, transaction_id)
            data.append(transaction)
        return data

    def extract_recurrence(self, cursor):
        print("     " + self.__class__.__name__)
        print("     " + "extract_recurrence()")
        data = []
        for category, amount, amount_frequency, recurrence_id, description, start_date, end_date, type, repeat_start_date, days_till_repeat in cursor:
            description = None if description == "null" else description
            if "period" in amount_frequency:
                continue
                recurrence = Period(category=category, amount=amount, start_date=start_date, end_date=end_date,
                                description=description, recurrence_id=recurrence_id)
            else:
                print("#HERE", description)
                tp = RecurrenceType.EXPENSE if type == 2 else RecurrenceType.INCOME
                recurrence = Recurrence(category=category, amount=amount, amount_frequency=amount_frequency,
                                    start_date=start_date, end_date=end_date, description=description, recurrence_id=recurrence_id, type=tp, repeat_start_date=repeat_start_date, days_till_repeat=days_till_repeat)

            if (repeat_start_date != None and repeat_start_date != "NULL" and repeat_start_date != "None"):
                data.append(recurrence)
        return data


    def get_min_max_transaction_dates(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_min_max_transaction_dates()")
        (self.db_conn, self.cursor) = self.get_instance()

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

        def months(start_month, start_year, end_month, end_year):
            print("Helper: months({},{},{},{})".format(start_month, start_year, end_month, end_year))

            start = datetime(start_year, start_month, 1)
            end = datetime(end_year, end_month, 1)
            return [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]

        return (min_year, months(min_month, min_year, max_month, max_year))

    def __exit__(self):
        print("in __exit__")