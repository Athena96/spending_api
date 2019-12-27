from datetime import datetime

from dateutil.rrule import rrule, MONTHLY
from flask import jsonify

from db_comms import DBComms
from models import RecurrenceType, SummaryPageInfo
from utilities import outside_to_python_transaction, python_to_outside_transaction


class DBCommsTransaction(DBComms):

    def __init__(self, database_path):
        DBComms.__init__(self, database_path)

    def add_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "add_transaction({})".format(transaction))
        (self.db_conn, self.cursor) = self.get_instance()

        writable_txn = python_to_outside_transaction(transaction)
        cmd = """INSERT INTO ledger (title, amount, category, date, description, var_txn_tracking, txn_type) VALUES ('{0}', {1}, '{2}', '{3}', '{4}', '{5}', {6})""".format(
            writable_txn["title"],
            writable_txn["amount"], writable_txn["category"], writable_txn["date"], writable_txn["description"],
            writable_txn["payment_method"], writable_txn["txn_type"])
        print(cmd)
        self.cursor.execute(cmd)
        self.db_conn.commit()
        self.db_conn.close()

        return jsonify({'result': 'successfully added transaction!'})

    def update_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "update_transaction({})".format(transaction))
        (self.db_conn, self.cursor) = self.get_instance()

        writable_txn = python_to_outside_transaction(transaction)
        cmd = """UPDATE ledger SET title = '{0}', amount = {1}, category = '{2}', date = '{3}', description = '{4}', var_txn_tracking = '{5}', txn_type = {6} WHERE ledger.transaction_id = {7}""".format(
            writable_txn["title"],
            writable_txn["amount"], writable_txn["category"], writable_txn["date"], writable_txn["description"],
            writable_txn["payment_method"], writable_txn["txn_type"], writable_txn["transaction_id"])
        print(cmd)
        self.cursor.execute(cmd)
        self.db_conn.commit()

        return jsonify({'result': 'successfully updated transaction!'})

    def delete_transaction(self, transaction_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_transaction({})", transaction_id)
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = "DELETE FROM ledger WHERE ledger.transaction_id = {0};".format(int(transaction_id))
        self.cursor.execute(cmd)
        self.db_conn.commit()
        print(cmd)

        return jsonify({'result': 'successfully deleted transaction!'})

    def get_transactions(self, year=None, month=None, category="ALL"):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction(month:{},year:{},category:{})".format(month, year, category))
        (self.db_conn, self.cursor) = self.get_instance()

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

    def get_auto_added_transaction_for_date(self, date):
        print("     " + self.__class__.__name__)
        print("     " + "get_auto_added_transaction_for_date(date:{})".format(date))
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = "select * from ledger where ledger.title like '[AUTO_ADDED]%' and ledger.date like '{}-{}-{}%'".format(
            date.year, date.month, date.day)
        print(cmd)
        self.cursor.execute(cmd)

        return self.extract_transactions(self.cursor)

    def get_categories(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_categories()")
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = "select distinct(ledger.category) from ledger order by ledger.category;"
        self.cursor.execute(cmd)

        return self.extract_categories(self.cursor)

    def get_spending(self, year, month):
        print("     " + self.__class__.__name__)
        print("     " + "get_spending()")
        if month is None or year is None:
            return ("--", "--")

        year_transactions = self.get_transactions(year=year)
        month_transactions = [transaction for transaction in year_transactions if (transaction.date[5:7] == month)]

        year_spent = round(sum([transaction.amount for transaction in year_transactions if
                                (transaction.txn_type == RecurrenceType.EXPENSE) and int(transaction.date[5:7]) <= int(
                                    month)]), 2)
        month_spent = round(sum([transaction.amount for transaction in month_transactions if
                                 (transaction.txn_type == RecurrenceType.EXPENSE)]), 2)

        return (year_spent, month_spent)

    def get_income(self, year, month):
        print("     " + self.__class__.__name__)
        print("     " + "get_income()")
        if month is None or year is None:
            return ("--", "--")

        year_transactions = self.get_transactions(year=year)

        year_income = round(sum([transaction.amount for transaction in year_transactions if
                                 (transaction.txn_type == RecurrenceType.INCOME) and int(transaction.date[5:7]) <= int(
                                     month)]), 2)
        month_income = round(sum([transaction.amount for transaction in year_transactions if
                                  (transaction.txn_type == RecurrenceType.INCOME) and (
                                          transaction.date[5:7] == month)]), 2)
        return (year_income, month_income)

    def get_transactions_by_payment_method(self, payment_method):
        print("     " + self.__class__.__name__)
        print("     " + "get_transactions_by_payment_method(payment_method:{})".format(payment_method))
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = "select * from ledger where ledger.var_txn_tracking like '{}'".format(payment_method)
        self.cursor.execute(cmd)

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

    def get_transaction_aggregations_category(self, year, month):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction_aggregations({},{})".format(year, month))
        if month is not None:
            cmd = """select A.category, A.month_total, B.year_total
            from (select ledger.category as 'category', sum(ledger.amount) as 'month_total'
                from ledger
                where ledger.date like( '%{}%')
                group by ledger.category) A, (select ledger.category  as 'category', sum(ledger.amount) as 'year_total'
                    from ledger
                    where ledger.date like('%{}%' )
                    group by ledger.category) B
            where A.category = B.category""".format("{}-{}-".format(year, month), "{}-".format(year))
        else:
            cmd = """select ledger.category  as 'category', 0.0 as 'month_total', sum(ledger.amount) as 'year_total'
            from ledger
            where ledger.date like('%{}%' )
            group by ledger.category
            order by year_total desc""".format("{}-".format(year))
        self.cursor.execute(cmd)

        aggregate_map = {}
        for category, month_total, year_total in self.cursor:
            aggregate_map[category] = SummaryPageInfo(category=category, spent_so_far_month=month_total,
                                                      spent_so_far_year=year_total)

        return aggregate_map

    def get_transaction_aggregations_payment_method(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction_payment_methods_aggregations()")
        cmd = """
        select A.var_txn_tracking as 'payment_method', A.amt as 'debit', ifnull(B.amt, 0.0) as 'credit', ifnull(A.amt, 0.0) - ifnull(B.amt, 0.0) as 'due'
        from
        (
        select ledger.var_txn_tracking as 'var_txn_tracking', ifnull(sum(ledger.amount),0.0) as 'amt'
        from ledger
        where ledger.txn_type = '2'  and ledger.var_txn_tracking like ('cc_%')
        group by ledger.var_txn_tracking
        ) A
        left join
        (
        select ledger.var_txn_tracking as 'var_txn_tracking', ifnull(sum(ledger.amount),0.0) as 'amt'
        from ledger
        where ledger.txn_type = '1'  and ledger.var_txn_tracking like ('cc_%')
        group by ledger.var_txn_tracking
        ) B
        on A.var_txn_tracking = B.var_txn_tracking
        order by payment_method;
        """
        self.cursor.execute(cmd)

        aggregate_map = {}
        for payment_method, debit, credit, due in self.cursor:
            aggregate_map[payment_method] = [payment_method, round(float(debit), 2), round(float(credit), 2),
                                             round(float(due), 2)]

        return aggregate_map

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

    def extract_transactions(self, cursor):
        print("     " + self.__class__.__name__)
        print("     " + "extract_transactions()")
        data = []
        for transaction_id, title, amount, category, date, description, payment_method, txn_type in cursor:
            transaction = outside_to_python_transaction(title=title, amount=amount, category=category, date=date,
                                                        description=description, payment_method=payment_method,
                                                        txn_type=txn_type, transaction_id=transaction_id)
            data.append(transaction)
        return data

    def extract_categories(self, cursor):
        print("     " + self.__class__.__name__)
        print("     " + "extract_categories()")

        data = []
        for category, in cursor:
            data.append(str(category))
        return data
