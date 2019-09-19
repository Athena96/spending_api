import calendar
from flask import Flask, jsonify, render_template
from datetime import datetime
from db_comms import DBCommms
from models import Category
from models import Transaction
from models import Budget
from models import Period
from models import BudgetPageInfo
from flask import current_app


# declare our Flask app
app = Flask(__name__)
# DATABASE = '/home/inherentVice/spending_log.db'

DATABASE = ""
with app.app_context():
    file = current_app.open_resource('path_to_DB.txt')
    DATABASE = file.read()


print("DATABASE", DATABASE)

# setup DB

# todo move all of these functions to a class? or what is the solution to having all     db_comm = DBCommms(DATABASE) in some constructor
#   todo so it works locally and on server
# Website page handlers: Transactions

@app.route("/site/transactions", methods=["GET"])
def transactions_root_page():
    print("transactions_root_page()")

    transaction_links = root_page_helper("transactions")
    return render_template('root_transactions.html', transaction_links=transaction_links)

@app.route("/site/add_transaction", methods=["GET"])
@app.route("/site/add_transaction/<string:transaction_id>", methods=["GET"])
def add_transaction_page(transaction_id=None):
    print("add_transaction_page()")
    db_comm = DBCommms(DATABASE)

    transaction = db_comm.get_transaction(transaction_id)
    budgets = db_comm.get_budgets(datetime.now())
    return render_template('add_transaction.html', transaction=transaction, budgets=budgets)

@app.route("/site/transactions/year:<string:year>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/category:<string:category>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>/category:<string:category>", methods=["GET"])
@app.route("/site/transactions/start_date:<string:start_date>/end_date:<string:end_date>/category:<string:category>", methods=["GET"])
def transactions_page(year=None, month=None, category="ALL", start_date=None, end_date=None):
    print("transactions_page()")
    db_comm = DBCommms(DATABASE)

    if start_date is not None and end_date is not None:
        sd = string_to_date(start_date)
        ed = string_to_date(end_date)

        # get transactions for period budget
        period_budget_period_transactions = db_comm.get_period_transactions(start_date=sd, end_date=ed, category=Category(name=category, is_income=False))

        return render_template('transactions.html',
        month=month, year=year,
        category=category,
        transactions=period_budget_period_transactions,
        spent_in_month=0.0, spent_in_year=0.0,
        month_income=0.0, year_income=0.0)

    year_transactions = db_comm.get_transactions(year=year, category=category)

    if month is not None:
        spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income) and int(transaction.date[5:7]) <= int(month)])
        (year_income, month_income) = calculate_income_from(year_transactions, month)
        month_transactions = [transaction for transaction in year_transactions if (transaction.date[5:7] == month)]
        spent_in_month = sum([transaction.amount for transaction in month_transactions if (not transaction.category[0].is_income)])
        spent_in_month_str = str(round(spent_in_month, 2))
    else:
        spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income)])
        (year_income, month_income) = ("--", "--")
        spent_in_month_str = "--"

    transactions = sorted(year_transactions if month is None else month_transactions, key=lambda x: x.date, reverse=True)

    txn_date_map = {}
    for txn in transactions:
        key = txn.get_transaction_day()
        if key not in txn_date_map.keys():
            txn_date_map[key] = []
        txn_date_map[key].append(txn)

    spent_in_year_str = str(round(spent_in_year, 2))
    return render_template('transactions.html',
    month=month, year=year,
    category=category,
    transactions=transactions,
    txn_date_map=txn_date_map,
    spent_in_month=spent_in_month_str, spent_in_year=spent_in_year_str,
    month_income=month_income, year_income=year_income)

# Website page handlers: Budgets

@app.route("/site/budgets", methods=["GET"])
def budgets_root_page():
    print("budgets_root_page()")

    budget_links = root_page_helper("budgets")
    return render_template('root_budgets.html', budget_links=budget_links)

@app.route("/site/add_budget", methods=["GET"])
@app.route("/site/add_budget/<string:budget_id>", methods=["GET"])
def add_budget_page(budget_id=None):
    print("add_budget_page()")
    db_comm = DBCommms(DATABASE)

    budget = db_comm.get_budget(budget_id)
    return render_template('add_budget.html', budget=budget)

@app.route("/site/budgets/year:<string:year>/month:<string:month>", methods=["GET"])
def budgets_page(year=None, month=None):
    print("budgets_page()")
    db_comm = DBCommms(DATABASE)

    today = datetime.now()
    if (year == today.year and month == today.month):
        budgets = db_comm.get_budgets(datetime.now())
    else:
        (start, end) = calendar.monthrange(int(year),int(month))
        budgets = db_comm.get_budgets(datetime(year=int(year), month=int(month), day=end))

    # getting transactions when we don't care about their category
    year_transactions = db_comm.get_transactions(year=year)

    spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income) and int(transaction.date[5:7]) <= int(month)])
    spent_in_year_str = str(round(spent_in_year, 2))

    month_transactions = [transaction for transaction in year_transactions if ((not transaction.category[0].is_income) and (transaction.date[5:7] == month))]
    spent_in_month = sum([transaction.amount for transaction in month_transactions])
    spent_in_month_str = str(round(spent_in_month, 2))

    (year_income, month_income) = calculate_income_from(year_transactions, month)

    budget_data = []
    for budget in budgets:

        if budget.category.is_income:
            continue

        budget_page_info = None
        if type(budget) is Period:
            sd = string_to_date(budget.start_date)
            ed = string_to_date(budget.end_date)
            # get transactions for period budget
            period_budget_period_transactions = db_comm.get_period_transactions(start_date=sd, end_date=ed, category=budget.category)
            spent_so_far_period = sum([transaction.amount for transaction in period_budget_period_transactions])

            filtered_year_category_transactions = list(filter(lambda transaction: (transaction.date[0:4] == year), period_budget_period_transactions))
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions])

            filtered_month_category_transactions = filter(lambda transaction: (transaction.date[5:7] == month), filtered_year_category_transactions)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

            budget_page_info = BudgetPageInfo(budget, spent_so_far_month, spent_so_far_year, spent_so_far_period)

        elif budget.amount_frequency == "month" or budget.amount_frequency == "year":
            # todo: just else... if its not a Period budget then it would have to be mo/year

            # this is getting transactions when we do care about their category!

            # use an SQL query here instead of matching in python.
                # querying for all transaction ID's with 'budget' ID from links table, join on Links and Txns
                # the func would be: get_transactions(category, year, month=None)

            filtered_year_category_transactions = list(filter(lambda transaction: (budget.category.name in transaction.get_categories()), year_transactions))
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions if int(transaction.date[5:7]) <= int(month)])

            filtered_month_category_transactions = filter(lambda transaction: (transaction.date[5:7] == month), filtered_year_category_transactions)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

            budget_page_info = BudgetPageInfo(budget, spent_so_far_month, spent_so_far_year)

        budget_data.append(budget_page_info)

    month_budgets = filter(lambda x: x.budget.amount_frequency == "month", budget_data)
    month_budgets = sorted(month_budgets, key=lambda x: x.budget.amount, reverse=True)

    year_budgets = filter(lambda x: x.budget.amount_frequency == "year", budget_data)
    year_budgets = sorted(year_budgets, key=lambda x: x.budget.amount, reverse=True)

    period_budgets = filter(lambda x: (type(x.budget) is Period), budget_data)
    period_budgets = sorted(period_budgets, key=lambda x: x.budget.amount, reverse=True)

    return render_template('budgets.html',
    month_budgets=month_budgets, year_budgets=year_budgets,
    period_budgets=period_budgets,
    month=month, year=year,
    spent_in_month=spent_in_month_str, spent_in_year=spent_in_year_str,
    month_income=month_income, year_income=year_income)

# Transaction API endpoints

@app.route('/transaction/<string:year>', methods=['GET'])
@app.route('/transaction/<string:month>/<string:year>/<string:category>', methods=['GET'])
def get_transactions(month=None, year=None, category="ALL"):
    print("get_all_transaction_for_year()")
    db_comm = DBCommms(DATABASE)

    return jsonify([transaction.to_dict() for transaction in db_comm.get_transactions(month,year,category)])

@app.route('/transaction/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['POST'])
def add_transaction(title, amount, category, date, description):
    print("add_transaction()")
    db_comm = DBCommms(DATABASE)

    description = None if description == "null" else description
    transaction = Transaction(title, amount, category, date, description)
    return db_comm.add_transaction(transaction)

@app.route('/transaction/<string:transaction_id>/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['PUT'])
def update_transaction(transaction_id, title, amount, category, date, description):
    print("update_transaction()")
    db_comm = DBCommms(DATABASE)

    transaction = Transaction(title, amount, category, date, description, transaction_id)
    return db_comm.update_transaction(transaction)

@app.route('/transaction/<string:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    print("delete_transaction()")
    db_comm = DBCommms(DATABASE)

    return db_comm.delete_transaction(transaction_id)

# Budget API endpoints

@app.route('/budgets', methods=['GET'])
def get_budgets():
    print("get_budgets()")
    db_comm = DBCommms(DATABASE)

    return jsonify([budget.to_dict() for budget in db_comm.get_budgets(datetime.now())])

@app.route('/budget/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>/<string:start_date>/<string:end_date>', methods=['POST'])
def add_budget(category, amount, amount_frequency, description, start_date, end_date):
    print("add_budget()")
    db_comm = DBCommms(DATABASE)

    description = None if description == "null" else description
    budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description)
    return db_comm.add_budget(budget)

@app.route('/budget/<string:budget_id>/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>/<string:start_date>/<string:end_date>', methods=['PUT'])
def update_budget(budget_id, category, amount, amount_frequency, description, start_date, end_date):
    print("update_budget()")
    db_comm = DBCommms(DATABASE)

    budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description, budget_id=budget_id)
    return db_comm.update_budget(budget)

@app.route('/budget/<string:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    print("delete_budget()")
    db_comm = DBCommms(DATABASE)

    return db_comm.delete_budget(budget_id)

# helpers
def get_curr_start_end(start_date, duration):
    print("Helper: get_curr_start_end({}, {})".format(start_date, duration))

    today = datetime.now()
    curr_start = start_date
    prev_start = None

    while today > curr_start:
        prev_start = curr_start
        curr_start = curr_start + duration

    return (prev_start, prev_start + duration)

def get_current_date():
    print("Helper: get_current_date()")

    year = "{}".format(datetime.now().year)
    curr_month = datetime.now().month
    month = single_digit_num_str(curr_month)
    return (month,year)

def single_digit_num_str(num):
    print("Helper: single_digit_num_str({})".format(num))

    str_num = ""
    if num < 10:
        str_num = "0{}".format(num)
    else:
        str_num = "{}".format(num)
    return str_num

def root_page_helper(type):
    print("Helper: root_page_helper({})".format(type))
    db_comm = DBCommms(DATABASE)

    (min_year, month_year_list) = db_comm.get_min_max_transaction_dates()

    final_year_links = []
    curr_year = min_year
    year_idx = 0
    year_first = True
    for (month,year) in month_year_list:
        if curr_year != year:
            curr_year = year
            year_idx += 1
            year_first = True

        month_str = single_digit_num_str(month)
        month_year_str = "{}-{}".format(month_str, year)
        link = "location.href='http://inherentvice.pythonanywhere.com/site/{}/year:{}/month:{}'".format(type, year, month_str)

        if year_first:
            final_year_links.append((year, []))
            year_first = False

        final_year_links[year_idx][1].append((month_year_str, link))

    return ((obj[0],(sorted(obj[1], reverse=True))) for obj in sorted(final_year_links, reverse=True))

def calculate_income_from(year_transactions, month):

    year_income = round(sum([transaction.amount for transaction in year_transactions if transaction.category[0].is_income and int(transaction.date[5:7]) <= int(month)]), 2)
    month_income = round(sum([transaction.amount for transaction in year_transactions if (transaction.category[0].is_income and (transaction.date[5:7] == month))]), 2)
    return (year_income, month_income)

def string_to_date(date_string):
    year = int(date_string.split("_")[0][0:4])
    month = int(date_string.split("_")[0][5:7])
    day = int(date_string.split("_")[0][8:10])
    return datetime(year=year, month=month, day=day)

if __name__ == '__main__':
    app.run()