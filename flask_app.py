from flask import Flask, jsonify, render_template
from dateutil.rrule import rrule, MONTHLY
from db_comms import DBCommms
from datetime import datetime
from datetime import timedelta
from models import Transaction
from models import Budget
from models import SpecialBudget

# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
db_comm = DBCommms(DATABASE)

# Website page handlers: Transactions

@app.route("/site/add_transaction", methods=["GET"])
@app.route("/site/add_transaction/<string:transaction_id>", methods=["GET"])
def add_transaction_page(transaction_id=None):
    print("add_transaction_page()")

    transaction = db_comm.get_transaction(transaction_id)
    budgets = db_comm.get_budgets()
    return render_template('add_transaction.html', transaction=transaction, budgets=budgets)

@app.route("/site/transactions", methods=["GET"])
def transactions_root_page():

    transaction_links = []

    cmd = """select min(ledger.date)
            from ledger"""
    db_comm.cursor.execute(cmd)
    min_date = db_comm.cursor.fetchone()[0]
    min_month = int(min_date[5:7])
    min_year = int(min_date[0:4])

    cmd = """select max(ledger.date)
            from ledger"""
    db_comm.cursor.execute(cmd)
    max_date = db_comm.cursor.fetchone()[0]
    max_month = int(max_date[5:7])
    max_year = int(max_date[0:4])

    print("min_date: " , min_date)
    print("max_date: " , max_date)

    for (m,y) in months(min_month, min_year, max_month, max_year):
        month_str = single_digit_num_str(m)
        # "location.href='http://inherentvice.pythonanywhere.com/site/transactions/{}/{}'".format()
        transaction_links.append(("location.href='http://inherentvice.pythonanywhere.com/site/transactions/{}/{}'".format(month_str, y), month_str, y))

    return render_template('root_transactions.html',
    transaction_links=transaction_links)

@app.route("/site/transactions/<string:month>/<string:year>", methods=["GET"])
@app.route("/site/transactions/<string:month>/<string:year>/<string:category>", methods=["GET"])
def transactions_page(month=None, year=None, category="ALL"):
    print("transactions_page()")

    year_transactions = db_comm.get_transactions(year=year, category=category)
    spent_in_year = sum([transaction.amount for transaction in year_transactions if ("income" not in transaction.category)])
    spent_in_year_str = str(round(spent_in_year, 2))

    month_transactions = [transaction for transaction in year_transactions if (transaction.date[5:7] == month)]
    spent_in_month = sum([transaction.amount for transaction in month_transactions if ("income" not in transaction.category)])
    spent_in_month_str = str(round(spent_in_month, 2))

    year_income = sum([transaction.amount for transaction in year_transactions if ("income" in transaction.category)])
    month_income = sum([transaction.amount for transaction in year_transactions if (("income" in transaction.category) and (transaction.date[5:7] == month))])

    transactions = sorted(month_transactions, key=lambda x: x.date, reverse=True)

    return render_template('transactions.html',
    month=month,
    year=year,
    category=category,
    transactions=transactions,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_income=month_income,
    year_income=year_income)

# Website page handlers: Budgets

@app.route("/site/add_budget", methods=["GET"])
@app.route("/site/add_budget/<string:budget_id>", methods=["GET"])
def add_budget_page(budget_id=None):
    print("add_budget_page()")

    budget = db_comm.get_budget(budget_id)
    return render_template('add_budget.html', budget=budget)

@app.route("/site/budgets", methods=["GET"])
def budgets_root_page():

    budgets_links = []

    cmd = """select min(ledger.date)
            from ledger"""
    db_comm.cursor.execute(cmd)
    min_date = db_comm.cursor.fetchone()[0]
    min_month = int(min_date[5:7])
    min_year = int(min_date[0:4])

    cmd = """select max(ledger.date)
            from ledger"""
    db_comm.cursor.execute(cmd)
    max_date = db_comm.cursor.fetchone()[0]
    max_month = int(max_date[5:7])
    max_year = int(max_date[0:4])

    print("min_date: " , min_date)
    print("max_date: " , max_date)

    for (m,y) in months(min_month, min_year, max_month, max_year):
        month_str = single_digit_num_str(m)
        # "location.href='http://inherentvice.pythonanywhere.com/site/budgets/{}/{}'".format()
        budgets_links.append(("location.href='http://inherentvice.pythonanywhere.com/site/budgets/{}/{}'".format(month_str, y), month_str, y))

    return render_template('root_budgets.html',
    budgets_links=budgets_links)

@app.route("/site/budgets/<string:month>/<string:year>", methods=["GET"])
def budgets_page(month=None, year=None):
    print("budgets_page()")

    budgets = db_comm.get_budgets()

    year_transactions = db_comm.get_transactions(year=year)
    spent_in_year = sum([transaction.amount for transaction in year_transactions if ("income" not in transaction.category)])
    spent_in_year_str = str(round(spent_in_year, 2))

    month_transactions = [transaction for transaction in year_transactions if (("income" not in transaction.category) and (transaction.date[5:7] == month))]
    spent_in_month = sum([transaction.amount for transaction in month_transactions])
    spent_in_month_str = str(round(spent_in_month, 2))

    year_income = sum([transaction.amount for transaction in year_transactions if ("income" in transaction.category)])
    month_income = sum([transaction.amount for transaction in year_transactions if (("income" in transaction.category) and (transaction.date[5:7] == month))])

    budget_data = []
    for budget in budgets:
        if "income" in budget.category:
            continue

        spent_so_far_str = ""

        if type(budget) is SpecialBudget:
            (s_year, s_month, s_day) = budget.start_date
            start_date = datetime(year=s_year, month=s_month, day=s_day)
            end_date = start_date + timedelta(days=budget.duration)

            print(budget.start_date)
            print(budget.duration)
            print(start_date)

            print(end_date)

            cmd = """select sum(ledger.amount)
            from ledger where ledger.category = '{0}'
            and ledger.date >= '{1}-{2}-{3} 00:00:00'
            and ledger.date <= '{4}-{5}-{6} 23:59:59'""".format(budget.category, s_year,
            '{:02d}'.format(s_month), '{:02d}'.format(s_day), end_date.year,
            '{:02d}'.format(end_date.month), '{:02d}'.format(end_date.day))
            db_comm.cursor.execute(cmd)

            spent_so_far = db_comm.cursor.fetchone()[0]
            if spent_so_far is None:
                spent_so_far = 0.0
            spent_so_far_str = "{}".format(round(spent_so_far, 2))

        elif budget.amount_frequency == "month" or budget.amount_frequency == "year":
            category_transactions = filter(lambda transaction: (transaction.category == budget.category), year_transactions)
            if budget.amount_frequency == "month":
                category_transactions = filter(lambda transaction: (transaction.date[5:7] == month), category_transactions)

            spent_so_far = sum([transaction.amount for transaction in category_transactions])
            spent_so_far_str = "{}".format(round(spent_so_far, 2))

        percent = -(spent_so_far / budget.amount)
        remaining = round((budget.amount + spent_so_far),2)

        entry = (budget.budget_id, budget.category, spent_so_far_str, percent, budget.amount, budget.amount_frequency, remaining)
        print("entry: ", entry)
        budget_data.append(entry)

    month_budgets = filter(lambda x: x[5] == "month", budget_data)
    month_budgets = sorted(month_budgets, key=lambda x: x[4])

    year_budgets = filter(lambda x: x[5] == "year", budget_data)
    year_budgets = sorted(year_budgets, key=lambda x: x[4])

    special_budgets = filter(lambda x: ("special" in x[5]), budget_data)
    special_budgets = sorted(special_budgets, key=lambda x: x[4])

    return render_template('budgets.html',
    month_budgets=month_budgets,
    year_budgets=year_budgets,
    special_budgets=special_budgets,
    month=month, year=year,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_income=month_income,
    year_income=year_income)

# Transaction API endpoints: Transactions

@app.route('/<string:year>', methods=['GET'])
@app.route('/<string:month>/<string:year>/<string:category>', methods=['GET'])
def get_transactions(month=None, year=None, category="ALL"):
    print("get_all_transaction_for_year()")

    result = jsonify([transaction.to_dict() for transaction in db_comm.get_transactions(month,year,category)])
    return result

@app.route('/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['POST'])
def add_transaction(title, amount, category, date, description):
    print("add_transaction()")

    transaction = Transaction(title, amount, category, date, description)
    result = db_comm.add_transaction(transaction)
    return result

@app.route('/<string:transaction_id>/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['PUT'])
def update_transaction(transaction_id, title, amount, category, date, description):
    print("update_transaction()")

    transaction = Transaction(title, amount, category, date, description, transaction_id)
    result = db_comm.update_transaction(transaction)
    return result

@app.route('/<string:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    print("delete_transaction()")

    result = db_comm.delete_transaction(transaction_id)
    return result

# Transaction API endpoints: Budgets

@app.route('/budgets', methods=['GET'])
def get_budgets():
    print("get_budgets()")

    result = jsonify([budget.to_dict() for budget in db_comm.get_budgets()])
    return result

@app.route('/budget/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>', methods=['POST'])
def add_budget(category, amount, amount_frequency, description):
    print("add_budget()")

    budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, description=description)
    result = db_comm.add_budget(budget)
    return result

@app.route('/budget/<string:budget_id>/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>', methods=['PUT'])
def update_budget(budget_id, category, amount, amount_frequency, description):
    print("update_budget()")

    budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, description=description, budget_id=budget_id)
    result = db_comm.update_budget(budget)
    return result

@app.route('/budget/<string:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    print("delete_budget()")

    result = db_comm.delete_budget(budget_id)
    return result

# helpers
def get_current_date():
    print("Helper: get_current_date()")

    year = "{}".format(datetime.now().year)
    curr_month = datetime.now().month
    month = single_digit_num_str(curr_month)
    return (month,year)

def single_digit_num_str(num):
    str_num = ""
    if num < 10:
        str_num = "0{}".format(num)
    else:
        str_num = "{}".format(num)
    return str_num

def months(start_month, start_year, end_month, end_year):
    start = datetime(start_year, start_month, 1)
    end = datetime(end_year, end_month, 1)
    return [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, until=end)]

