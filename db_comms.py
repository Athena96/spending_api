from flask import jsonify
from models import Transaction
from models import Budget

import sqlite3

# -- Month budgets
# 	select budget.category, budget.amount, sum(ledger.amount) as spent, (budget.amount + sum(ledger.amount)) as remaining
# 	from budget
# 	left join ledger
# 	on budget.category = ledger.category
# 	where budget.amount_frequency like('month') and ledger.date like('2019-04%')
# 	group by budget.category

# union

# 	select budget.category, budget.amount, '0.00' as spent, budget.amount as remaining
# 	from budget
# 	where budget.amount_frequency like('month')
# 	and budget.category not in (
# 		select budget.category
# 		from budget
# 		left join ledger
# 		on budget.category = ledger.category
# 		where budget.amount_frequency like('month') and ledger.date like('2019-04%')
# 		group by budget.category
# 	)
# -- Year Budgets


# 	select budget.category, budget.amount, sum(ledger.amount) as spent, (budget.amount + sum(ledger.amount)) as remaining
# 	from budget
# 	left join ledger
# 	on budget.category = ledger.category
# 	where budget.amount_frequency like('year') and ledger.date like('2019-%')
# 	group by budget.category

# union

# 	select budget.category, budget.amount, '0.00' as spent, budget.amount as remaining
# 	from budget
# 	where budget.amount_frequency like('year')
# 	and budget.category not in (
# 		select budget.category
# 		from budget
# 		left join ledger
# 		on budget.category = ledger.category
# 		where budget.amount_frequency like('year') and ledger.date like('2019-%')
# 		group by budget.category
# 	)


# -- Special Budgets



# 	select budget.category, budget.amount, sum(ledger.amount) as spent, (budget.amount + sum(ledger.amount)) as remaining
# 	from budget
# 	left join ledger
# 	on budget.category = ledger.category
# 	where budget.amount_frequency like('special') and ledger.date >=
# 	group by budget.category

# union

# 	select budget.category, budget.amount, '0.00' as spent, budget.amount as remaining
# 	from budget
# 	where budget.amount_frequency like('special')
# 	and budget.category not in (
# 		select budget.category
# 		from budget
# 		left join ledger
# 		on budget.category = ledger.category
# 		where budget.amount_frequency like('special') and ledger.date like('2019-%')
# 		group by budget.category
# 	)



class DBCommms:

    def __init__(self, database_path):
        self.database_path = database_path
        self.db_conn = sqlite3.connect(database_path)
        self.cursor = self.db_conn.cursor()

    # Transaction Methods

    # add, update, delete
    def add_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "add_transaction({})".format(transaction))

        # add transaction
        sql_note = "NULL" if (transaction.note == None) else "'{0}'".format(transaction.note)

        cmd = """INSERT INTO ledger (title, amount, category, date, note) VALUES ('{0}', {1}, '{2}', '{3}', {4})""".format(transaction.title,
            transaction.amount, transaction.category, transaction.date, sql_note)
        print(cmd)
        self.cursor.execute(cmd)

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added transaction!'})

    def update_transaction(self, transaction):
        print("     " + self.__class__.__name__)
        print("     " + "update_transaction({})".format(transaction))

        sql_note = "NULL" if (transaction.note == None) else "'{0}'".format(transaction.note)

        cmd = """UPDATE ledger SET title = '{0}', amount = {1}, category = '{2}', date = '{3}', note = {4} WHERE ledger.transaction_id = {5}""".format(transaction.title,
        transaction.amount, transaction.category, transaction.date, sql_note, transaction.transaction_id)
        print(cmd)
        self.cursor.execute(cmd)

        self.db_conn.commit()

        return jsonify({'result': 'successfuly updated transaction!'})

    def delete_transaction(self, transaction_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_transaction({})", transaction_id)

        self.cursor.execute("DELETE FROM ledger WHERE ledger.transaction_id = {0};".format(int(transaction_id)))
        self.db_conn.commit()

        return jsonify({'result': 'successfuly deleted transaction!'})

    # fetch
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

        q = base_query + " where " + date_query + (" and " if category != "ALL" else "") + category_query
        print("     " + q)

        self.cursor.execute(q)

        data = []
        for transaction_id, title, amount, category, date, note in self.cursor:
            transaction = Transaction(title, amount, category, date, note, transaction_id)
            data.append(transaction)

        # send data
        return data

    def get_transaction(self, transaction_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_transaction({})".format(transaction_id))
        if transaction_id is None:
            return None

        self.cursor.execute("SELECT * FROM ledger where ledger.transaction_id = {}".format(transaction_id))

        res = None
        for transaction_id, title, amount, category, date, note in  self.cursor:
            res = Transaction(title, amount, category, date, note, transaction_id)

        # send data
        return res


    # Budget Methods

    # add, update, delete
    def add_budget_category(self, budget):
        print("     " + self.__class__.__name__)
        print("     " + "add_budget_category({})", budget)

        sql_description = "NULL" if (budget.description == None) else "'{0}'".format(budget.description)

        # add budget category
        cmd = """INSERT INTO budget (category, amount, amount_frequency, description) VALUES ('{0}', {1}, '{2}', {3})""".format(budget.category, budget.amount, budget.amount_frequency, sql_description)
        print(cmd)
        self.cursor.execute(cmd)

        self.db_conn.commit()

        return jsonify({'result': 'successfuly added budget category!'})

    def update_budget_category(self, budget):
        print("     " + self.__class__.__name__)
        print("     " + "update_budget_category({})", budget)

        sql_description = "NULL" if (budget.description == None) else "'{0}'".format(budget.description)

        cmd = """UPDATE budget SET category = '{0}', amount = {1}, amount_frequency = '{2}', description = {3} WHERE budget.category_id = {4}""".format(budget.category,
        budget.amount, budget.amount_frequency, sql_description, budget.budget_id)
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
        for category, amount, amount_frequency, category_id, description in self.cursor:
            budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, description=description, budget_id=category_id)
            print("get_budgets: ", (category, amount, amount_frequency, description, category_id))
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
        for category, amount, amount_frequency, category_id, description in self.cursor:
            res = Budget(category=category, amount=amount, amount_frequency=amount_frequency, description=description, budget_id=category_id)

        # send data
        return res


    def __exit__(self):
        print("in __exit__")
