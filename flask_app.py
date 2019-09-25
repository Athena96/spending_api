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
from utilities import string_to_date, calculate_income_from

#todo db_comm function to return spent_in_month, spent_in_year and month_income and year_income

# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = ""
ENVIRONMENT = ""
db_comm = None
with app.app_context():
    file = current_app.open_resource('path_to_DB.txt')
    DATABASE = str(file.read().decode("utf-8")).replace('\n','')
    db_comm = DBCommms(DATABASE)
    if "inherentVice" in DATABASE:
        ENVIRONMENT = "http://inherentvice.pythonanywhere.com"
    else:
        ENVIRONMENT = "http://127.0.0.1:5000"

# Website page handlers: Transactions

@app.route("/site/transactions", methods=["GET"])
def transactions_root_page():
    print("transactions_root_page()")

    transaction_links = get_date_page_links("transactions")
    return render_template('root_transactions.html', transaction_links=transaction_links, prefix=ENVIRONMENT)

@app.route("/site/add_transaction", methods=["GET"])
@app.route("/site/add_transaction/<string:transaction_id>", methods=["GET"])
def add_transaction_page(transaction_id=None):
    print("add_transaction_page()")
    
    transaction = db_comm.get_transaction(transaction_id)
    budgets = db_comm.get_budgets(datetime.now())
    return render_template('add_transaction.html', transaction=transaction, budgets=budgets, prefix=ENVIRONMENT)

@app.route("/site/transactions/year:<string:year>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/category:<string:category>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>/category:<string:category>", methods=["GET"])
@app.route("/site/transactions/start_date:<string:start_date>/end_date:<string:end_date>/category:<string:category>", methods=["GET"])
def transactions_page(year=None, month=None, category="ALL", start_date=None, end_date=None):
    print("transactions_page()")

    # if displaying only transactions between certain period
    if start_date is not None and end_date is not None:
        sd = string_to_date(start_date)
        ed = string_to_date(end_date)

        # get transactions for period budget
        period_budget_period_transactions = db_comm.get_transactions_between(start_date=sd, end_date=ed, category=Category(name=category, is_income=False))

        return render_template('transactions.html',
        month=month, year=year,
        category=category,
        transactions=period_budget_period_transactions,
        spent_in_month=0.0, spent_in_year=0.0,
        month_income=0.0, year_income=0.0, prefix=ENVIRONMENT)

    # 1 get all the year transactions
    year_transactions = db_comm.get_transactions(year=year, category=category)

    # 2 get year and month income values
    (year_income, month_income) = calculate_income_from(year_transactions, month)

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


    # sort the transactions to display and store them in "transactions"
    transactions = sorted(year_transactions if month is None else month_transactions, key=lambda x: x.date, reverse=True)

    # create date map to group txns by day
    txn_date_map = {}
    for txn in transactions:
        key = txn.get_transaction_day_date()
        if key not in txn_date_map.keys():
            txn_date_map[key] = []
        txn_date_map[key].append(txn)

    return render_template('transactions.html',
    month=month, year=year,
    category=category,
    transactions=transactions,
    txn_date_map_keys=sorted(txn_date_map.keys(),reverse=True),
    txn_date_map=txn_date_map,
    spent_in_month=spent_in_month_str, spent_in_year=spent_in_year_str,
    month_income=month_income, year_income=year_income, prefix=ENVIRONMENT)

# Website page handlers: Budgets

@app.route("/site/budgets", methods=["GET"])
def budgets_root_page():
    print("budgets_root_page()")

    budget_links = get_date_page_links("budgets")
    return render_template('root_budgets.html', budget_links=budget_links, prefix=ENVIRONMENT)

@app.route("/site/add_budget", methods=["GET"])
@app.route("/site/add_budget/<string:budget_id>", methods=["GET"])
def add_budget_page(budget_id=None):
    print("add_budget_page()")
    budget = db_comm.get_budget(budget_id)
    return render_template('add_budget.html', budget=budget, prefix=ENVIRONMENT)

@app.route("/site/budgets/year:<string:year>/month:<string:month>", methods=["GET"])
def budgets_page(year=None, month=None):
    print("budgets_page()")

    # get the budgets for the requested year/month
    (start, end) = calendar.monthrange(int(year), int(month))
    budgets = db_comm.get_budgets(datetime(year=int(year), month=int(month), day=end))

    # 1 get all the year transactions
    year_transactions = db_comm.get_transactions(year=year)

    # 2 get year and month income values
    (year_income, month_income) = calculate_income_from(year_transactions, month)

    # 3 filter month transactions
    month_transactions = [transaction for transaction in year_transactions if ((not transaction.category[0].is_income) and (transaction.date[5:7] == month))]

    # 4 calculate spent_in_year
    spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income) and int(transaction.date[5:7]) <= int(month)])
    spent_in_year_str = str(round(spent_in_year, 2))

    # 5 calculate spent_in_month
    spent_in_month = sum([transaction.amount for transaction in month_transactions])
    spent_in_month_str = str(round(spent_in_month, 2))

    budget_data = []
    for budget in budgets:

        if budget.category.is_income:
            continue

        if type(budget) is Period or budget.amount_frequency == "period":
            sd = string_to_date(budget.start_date)
            ed = string_to_date(budget.end_date)
            # get transactions for period budget
            period_budget_period_transactions = db_comm.get_transactions_between(start_date=sd, end_date=ed, category=budget.category)
            spent_so_far_period = sum([transaction.amount for transaction in period_budget_period_transactions])

            filtered_year_category_transactions = list(filter(lambda transaction: (transaction.date[0:4] == year), period_budget_period_transactions))
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions])

            filtered_month_category_transactions = filter(lambda transaction: (transaction.date[5:7] == month), filtered_year_category_transactions)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

        elif budget.amount_frequency == "month" or budget.amount_frequency == "year":
            spent_so_far_period = None
            filtered_year_category_transactions = db_comm.get_transactions(year=year, category=budget.category.name)
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions if int(transaction.date[5:7]) <= int(month)])

            filtered_month_category_transactions = db_comm.get_transactions(year=year, month=month, category=budget.category.name)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

        budget_data.append( BudgetPageInfo(budget, spent_so_far_month, spent_so_far_year, spent_so_far_period) )

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
    month_income=month_income, year_income=year_income, prefix=ENVIRONMENT)

# Transaction API endpoints

@app.route('/transactions/<string:year>', methods=['GET'])
@app.route('/transactions/<string:year>/<string:month>/<string:category>', methods=['GET'])
def get_transactions(year=None, month=None, category="ALL"):
    print("[api] get_transactions()")

    return jsonify([transaction.to_dict() for transaction in db_comm.get_transactions(year, month, category)])

@app.route('/transactions/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['POST'])
def add_transaction(title, amount, category, date, description):
    print("[api] add_transaction()")

    description = None if description == "null" else description
    transaction = Transaction(title, amount, category, date, description)
    return db_comm.add_transaction(transaction)

@app.route('/transactions/<string:transaction_id>/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['PUT'])
def update_transaction(transaction_id, title, amount, category, date, description):
    print("[api] update_transaction()")

    transaction = Transaction(title, amount, category, date, description, transaction_id)
    return db_comm.update_transaction(transaction)

@app.route('/transactions/<string:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    print("[api] delete_transaction()")

    return db_comm.delete_transaction(transaction_id)

# Budget API endpoints

@app.route('/budgets', methods=['GET'])
def get_budgets():
    print("[api] get_budgets()")

    return jsonify([budget.to_dict() for budget in db_comm.get_budgets(datetime.now())])

@app.route('/budgets/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>/<string:start_date>/<string:end_date>', methods=['POST'])
def add_budget(category, amount, amount_frequency, description, start_date, end_date):
    print("[api] add_budget()")

    description = None if description == "null" else description
    budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description)
    return db_comm.add_budget(budget)

@app.route('/budgets/<string:budget_id>/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>/<string:start_date>/<string:end_date>', methods=['PUT'])
def update_budget(budget_id, category, amount, amount_frequency, description, start_date, end_date):
    print("[api] update_budget()")

    budget = Budget(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description, budget_id=budget_id)
    return db_comm.update_budget(budget)

@app.route('/budgets/<string:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    print("[api] delete_budget()")

    return db_comm.delete_budget(budget_id)

# helpers
def get_date_page_links(type):
    print("Helper: root_page_helper({})".format(type))

    (min_year, month_year_list) = db_comm.get_min_max_transaction_dates()
    final_year_links = []
    curr_year = min_year
    year_idx = 0
    year_first = True
    for (month, year) in month_year_list:
        if curr_year != year:
            curr_year = year
            year_idx += 1
            year_first = True

        month_str = "{:02d}".format(month)
        month_year_str = "{}-{}".format(month_str, year)
        link = "location.href='{}/site/{}/year:{}/month:{}'".format(ENVIRONMENT, type, year, month_str)

        if year_first:
            final_year_links.append((year, []))
            year_first = False

        final_year_links[year_idx][1].append((month_year_str, link))

    return ((obj[0],(sorted(obj[1], reverse=True))) for obj in sorted(final_year_links, reverse=True))
