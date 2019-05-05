from flask import Flask, jsonify, render_template
from datetime import datetime
from datetime import timedelta
from db_comms import DBCommms
from models import Category
from models import Transaction
from models import Budget
from models import SpecialBudget
from models import BudgetPageInfo

# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
db_comm = DBCommms(DATABASE)

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

    transaction = db_comm.get_transaction(transaction_id)
    budgets = db_comm.get_budgets()
    return render_template('add_transaction.html', transaction=transaction, budgets=budgets)

@app.route("/site/transactions/special_category:<string:special_category>/special_frequency:<string:special_frequency>/", methods=["GET"])
@app.route("/site/transactions/year:<string:year>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/category:<string:category>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>/category:<string:category>", methods=["GET"])
def transactions_page(year=None, month=None, category="ALL", special_category=None, special_frequency=None):
    print("transactions_page()")

    if special_category is not None and special_frequency is not None:
        print("SPECIAL")
        s_duration = int(special_frequency.split("_")[2])
        startdate = special_frequency.split("_")[1]
        s_year = int(startdate[0:4])
        s_month = int(startdate[4:6])
        s_day = int(startdate[6:8])
        print(s_year, s_month, s_day)

        # get original start date and duration
        start_date = datetime(year=s_year, month=s_month, day=s_day)
        duration = timedelta(days=s_duration)

        # get new start and end date that it currently falls in
        (start_date, end_date) = get_curr_start_end(start_date, duration)

        # get transactions for special budget
        special_budget_period_transactions = db_comm.get_special_transactions(start_date=start_date, end_date=end_date, category=Category(name=special_category, is_income=False))

        return render_template('transactions.html',
        month=month,
        year=year,
        category=special_category,
        transactions=special_budget_period_transactions,
        spent_in_month=0.0,
        spent_in_year=0.0,
        month_income=0.0,
        year_income=0.0)

    year_transactions = db_comm.get_transactions(year=year, category=category)
    spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income)])
    spent_in_year_str = str(round(spent_in_year, 2))

    year_income = sum([transaction.amount for transaction in year_transactions if transaction.category[0].is_income])
    month_income = sum([transaction.amount for transaction in year_transactions if (transaction.category[0].is_income and (transaction.date[5:7] == month))])

    spent_in_month_str = "0.00"
    if month is not None:
        month_transactions = [transaction for transaction in year_transactions if (transaction.date[5:7] == month)]
        spent_in_month = sum([transaction.amount for transaction in month_transactions if (not transaction.category[0].is_income)])
        spent_in_month_str = str(round(spent_in_month, 2))

    transactions = sorted(year_transactions if month is None else month_transactions, key=lambda x: x.date, reverse=True)

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

@app.route("/site/budgets", methods=["GET"])
def budgets_root_page():
    print("budgets_root_page()")
    budget_links = root_page_helper("budgets")
    return render_template('root_budgets.html', budget_links=budget_links)

@app.route("/site/add_budget", methods=["GET"])
@app.route("/site/add_budget/<string:budget_id>", methods=["GET"])
def add_budget_page(budget_id=None):
    print("add_budget_page()")

    budget = db_comm.get_budget(budget_id)
    return render_template('add_budget.html', budget=budget)

@app.route("/site/budgets/year:<string:year>/month:<string:month>", methods=["GET"])
def budgets_page(year=None, month=None):
    print("budgets_page()")
    budgets = db_comm.get_budgets()

    year_transactions = db_comm.get_transactions(year=year)
    spent_in_year = sum([transaction.amount for transaction in year_transactions if (not transaction.category[0].is_income)])
    spent_in_year_str = str(round(spent_in_year, 2))

    month_transactions = [transaction for transaction in year_transactions if ((not transaction.category[0].is_income) and (transaction.date[5:7] == month))]
    spent_in_month = sum([transaction.amount for transaction in month_transactions])
    spent_in_month_str = str(round(spent_in_month, 2))

    year_income = sum([transaction.amount for transaction in year_transactions if transaction.category[0].is_income])
    month_income = sum([transaction.amount for transaction in year_transactions if (transaction.category[0].is_income and (transaction.date[5:7] == month))])

    budget_data = []
    for budget in budgets:

        if budget.category.is_income:
            continue

        b = None
        if type(budget) is SpecialBudget:

            # get original start date and duration
            (s_year, s_month, s_day) = budget.start_date
            start_date = datetime(year=s_year, month=s_month, day=s_day)
            duration = timedelta(days=budget.duration)

            # get new start and end date that it currently falls in
            (start_date, end_date) = get_curr_start_end(start_date, duration)

            # get transactions for special budget
            special_budget_period_transactions = db_comm.get_special_transactions(start_date=start_date, end_date=end_date, category=budget.category)
            spent_so_far_period = sum([transaction.amount for transaction in special_budget_period_transactions])

            filtered_year_category_transactions = list(filter(lambda transaction: (transaction.date[0:4] == year), special_budget_period_transactions))
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions])

            filtered_month_category_transactions = filter(lambda transaction: (transaction.date[5:7] == month), filtered_year_category_transactions)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

            b = BudgetPageInfo(budget, spent_so_far_month, spent_so_far_year, spent_so_far_period)

        elif budget.amount_frequency == "month" or budget.amount_frequency == "year":
            filtered_year_category_transactions = list(filter(lambda transaction: (budget.category.name in transaction.get_categories()), year_transactions))
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions])

            filtered_month_category_transactions = filter(lambda transaction: (transaction.date[5:7] == month), filtered_year_category_transactions)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

            b = BudgetPageInfo(budget, spent_so_far_month, spent_so_far_year)

        budget_data.append(b)

    month_budgets = filter(lambda x: x.budget.amount_frequency == "month", budget_data)
    month_budgets = sorted(month_budgets, key=lambda x: x.budget.amount, reverse=True)

    year_budgets = filter(lambda x: x.budget.amount_frequency == "year", budget_data)
    year_budgets = sorted(year_budgets, key=lambda x: x.budget.amount, reverse=True)

    special_budgets = filter(lambda x: (type(x.budget) is SpecialBudget), budget_data)
    special_budgets = sorted(special_budgets, key=lambda x: x.budget.amount, reverse=True)

    return render_template('budgets.html',
    month_budgets=month_budgets,
    year_budgets=year_budgets,
    special_budgets=special_budgets,
    month=month, year=year,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_income=month_income,
    year_income=year_income)

# Transaction API endpoints

@app.route('/transaction/<string:year>', methods=['GET'])
@app.route('/transaction/<string:month>/<string:year>/<string:category>', methods=['GET'])
def get_transactions(month=None, year=None, category="ALL"):
    print("get_all_transaction_for_year()")

    result = jsonify([transaction.to_dict() for transaction in db_comm.get_transactions(month,year,category)])
    return result

@app.route('/transaction/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['POST'])
def add_transaction(title, amount, category, date, description):
    print("add_transaction()")

    description = None if description == "null" else description
    transaction = Transaction(title, amount, category, date, description)
    result = db_comm.add_transaction(transaction)
    return result

@app.route('/transaction/<string:transaction_id>/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>', methods=['PUT'])
def update_transaction(transaction_id, title, amount, category, date, description):
    print("update_transaction()")

    transaction = Transaction(title, amount, category, date, description, transaction_id)
    result = db_comm.update_transaction(transaction)
    return result

@app.route('/transaction/<string:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    print("delete_transaction()")

    result = db_comm.delete_transaction(transaction_id)
    return result

# Budget API endpoints

@app.route('/budgets', methods=['GET'])
def get_budgets():
    print("get_budgets()")

    result = jsonify([budget.to_dict() for budget in db_comm.get_budgets()])
    return result

@app.route('/budget/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>', methods=['POST'])
def add_budget(category, amount, amount_frequency, description):
    print("add_budget()")

    description = None if description == "null" else description
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
def get_curr_start_end(start_date, duration):
    print("Helper: get_curr_start_end()")
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
    print("Helper: single_digit_num_str()")
    str_num = ""
    if num < 10:
        str_num = "0{}".format(num)
    else:
        str_num = "{}".format(num)
    return str_num

def root_page_helper(type):
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
