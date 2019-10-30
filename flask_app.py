import calendar
from flask import Flask, jsonify, render_template
from datetime import datetime
from db_comms import DBCommms
from models import Category
from models import Transaction
from models import Recurrence
from models import Period
from models import RecurrencePageInfo
from timeline_generator import TimelineGenerator
from flask import current_app
from utilities import string_to_date
from utilities import is_valid_or_none
from utilities import get_variable_recurrence_transactions
from models import RecurrenceType

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

# Website page handlers: Timeline

@app.route("/site/timeline", methods=["GET"])
def timeline_page():
    print("timeline_page()")
    recurrences = db_comm.get_recurrences(datetime.now())
    generator = TimelineGenerator(months_to_generate=4, db_comm=db_comm, initial_recurrences=recurrences)
    table = generator.generate_table()
    last_day_bal_num = round(table[len(table)-1].balance,2)
    last_day_bal = "${}".format(last_day_bal_num)
    last_day_bal_dff = "${}".format(round((last_day_bal_num-2374.75), 2))
    return render_template('timeline.html', timeline_table=table, last_day_bal=last_day_bal, last_day_bal_dff=last_day_bal_dff, prefix=ENVIRONMENT)

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
    recurrences = db_comm.get_recurrences(datetime.now())
    return render_template('add_transaction.html', transaction=transaction, recurrences=recurrences, prefix=ENVIRONMENT)

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

        # get transactions for period recurrence
        period_recurrence_period_transactions = db_comm.get_transactions_between(start_date=sd, end_date=ed, category=Category(name=category, is_income=False))

        return render_template('transactions.html',
        month=month, year=year,
        category=category,
        transactions=period_recurrence_period_transactions,
        spent_in_month=0.0, spent_in_year=0.0,
        month_income=0.0, year_income=0.0, prefix=ENVIRONMENT)

    # get all the year transactions (and filter month as well)
    year_transactions = db_comm.get_transactions(year=year, category=category)
    month_transactions = [transaction for transaction in year_transactions if (transaction.date[5:7] == month)]

    # 2 get year and month income/spending values
    (year_income, month_income) = db_comm.get_income(year, month)
    (spent_in_year_str, spent_in_month_str) = db_comm.get_spending(year, month)

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

# Website page handlers: Recurrence

@app.route("/site/recurrences", methods=["GET"])
def recurrences_root_page():
    print("recurrences_root_page()")

    recurrence_links = get_date_page_links("recurrences")
    return render_template('root_recurrences.html', recurrence_links=recurrence_links, prefix=ENVIRONMENT)

@app.route("/site/add_recurrence", methods=["GET"])
@app.route("/site/add_recurrence/<string:recurrence_id>", methods=["GET"])
def add_recurrence_page(recurrence_id=None):
    print("add_recurrence_page()")
    recurrence = db_comm.get_recurrence(recurrence_id)
    return render_template('add_recurrence.html', recurrence=recurrence, prefix=ENVIRONMENT)

@app.route("/site/recurrences/year:<string:year>/month:<string:month>", methods=["GET"])
def recurrence_page(year=None, month=None):
    print("recurrences_page()")

    # get the recurrences for the requested year/month
    (start, end) = calendar.monthrange(int(year), int(month))
    recurrences = db_comm.get_recurrences(datetime(year=int(year), month=int(month), day=end))
    print("RECURRENCES: ", [x.category.name for x in recurrences])

    # 2 get year and month income/spending values
    (year_income, month_income) = db_comm.get_income(year, month)
    (spent_in_year_str, spent_in_month_str) = db_comm.get_spending(year, month)

    recurrence_data = []
    for recurrence in recurrences:

        if recurrence.category.is_income:
            continue

        if type(recurrence) is Period or recurrence.amount_frequency == "period":
            sd = string_to_date(recurrence.start_date)
            ed = string_to_date(recurrence.end_date)
            # get transactions for period recurrence
            period_recurrence_period_transactions = db_comm.get_transactions_between(start_date=sd, end_date=ed, category=recurrence.category)
            spent_so_far_period = sum([transaction.amount for transaction in period_recurrence_period_transactions])

            filtered_year_category_transactions = list(filter(lambda transaction: (transaction.date[0:4] == year), period_recurrence_period_transactions))
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions])

            filtered_month_category_transactions = filter(lambda transaction: (transaction.date[5:7] == month), filtered_year_category_transactions)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

        elif recurrence.amount_frequency == "month" or recurrence.amount_frequency == "year":
            spent_so_far_period = None
            filtered_year_category_transactions = db_comm.get_transactions(year=year, category=recurrence.category.name)
            spent_so_far_year = sum([transaction.amount for transaction in filtered_year_category_transactions if int(transaction.date[5:7]) <= int(month)])

            filtered_month_category_transactions = db_comm.get_transactions(year=year, month=month, category=recurrence.category.name)
            spent_so_far_month = sum([transaction.amount for transaction in filtered_month_category_transactions])

        elif recurrence.amount_frequency == "variable":

            # get transactions for period recurrence
            period_recurrence_period_transactions = get_variable_recurrence_transactions(db_comm, recurrence)
            spent_so_far_period = sum([transaction.amount for transaction in period_recurrence_period_transactions])
            recurrence.amount = spent_so_far_period
            spent_so_far_year = 0.0
            spent_so_far_month = 0.0


        recurrence_data.append(RecurrencePageInfo(recurrence, spent_so_far_month, spent_so_far_year, spent_so_far_period))

    month_recurrences = filter(lambda x: x.recurrence.amount_frequency == "month", recurrence_data)
    month_recurrences = sorted(month_recurrences, key=lambda x: x.recurrence.amount, reverse=True)

    year_recurrences = filter(lambda x: x.recurrence.amount_frequency == "year", recurrence_data)
    year_recurrences = sorted(year_recurrences, key=lambda x: x.recurrence.amount, reverse=True)

    variable_recurrences = filter(lambda x: x.recurrence.amount_frequency == "variable", recurrence_data)
    variable_recurrences = sorted(variable_recurrences, key=lambda x: x.recurrence.amount, reverse=True)

    period_recurrences = filter(lambda x: (type(x.recurrence) is Period), recurrence_data)
    period_recurrences = sorted(period_recurrences, key=lambda x: x.recurrence.amount, reverse=True)

    return render_template('recurrences.html',
    month_recurrences=month_recurrences, year_recurrences=year_recurrences,
    period_recurrences=period_recurrences,
    variable_recurrences=variable_recurrences,
    month=month, year=year,
    spent_in_month=spent_in_month_str, spent_in_year=spent_in_year_str,
    month_income=month_income, year_income=year_income, prefix=ENVIRONMENT)

# Transaction API endpoints

@app.route('/transactions/<string:year>', methods=['GET'])
@app.route('/transactions/<string:year>/<string:month>/<string:category>', methods=['GET'])
def get_transactions(year=None, month=None, category="ALL"):
    print("[api] get_transactions()")

    return jsonify([transaction.to_dict() for transaction in db_comm.get_transactions(year, month, category)])

@app.route('/transactions/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>/<string:credit_card>', methods=['POST'])
def add_transaction(title, amount, category, date, description, credit_card):
    print("[api] add_transaction()")
    # todo 1) send null txID here, 2) abstract out the duplicate code here and in update_transaction
    description = None if description == "null" else description
    credit_card = None if is_valid_or_none(credit_card) is None else credit_card
    transaction = Transaction(title=title, amount=amount, category=category, date=date, description=description, credit_card=credit_card)
    return db_comm.add_transaction(transaction)

@app.route('/transactions/<string:transaction_id>/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>/<string:credit_card>', methods=['PUT'])
def update_transaction(transaction_id, title, amount, category, date, description, credit_card):
    print("[api] update_transaction()")
    description = None if description == "null" else description
    credit_card = None if is_valid_or_none(credit_card) is None else credit_card
    transaction = Transaction(title=title, amount=amount, category=category, date=date, description=description, transaction_id=transaction_id, credit_card=credit_card)
    return db_comm.update_transaction(transaction)

@app.route('/transactions/<string:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    print("[api] delete_transaction()")

    return db_comm.delete_transaction(transaction_id)

# Recurrence API endpoints

@app.route('/recurrences', methods=['GET'])
def get_recurrences():
    print("[api] get_recurrences()")

    return jsonify([recurrence.to_dict() for recurrence in db_comm.get_recurrences(datetime.now())])

@app.route('/recurrence/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>/<string:start_date>/<string:end_date>/<string:type>/<string:repeat_start_date>/<string:days_till_repeat>', methods=['POST'])
def add_recurrence(category, amount, amount_frequency, description, start_date, end_date, type, repeat_start_date, days_till_repeat):
    print("[api] add_recurrence()")

    description = None if description == "null" else description
    repeat_start_date = None if is_valid_or_none(repeat_start_date) is None else string_to_date(repeat_start_date)
    description = None if is_valid_or_none(description) is None else description
    tp = RecurrenceType.EXPENSE if type == 2 else RecurrenceType.INCOME

    recurrence = Recurrence(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description, type=tp, repeat_start_date=repeat_start_date, days_till_repeat=days_till_repeat)
    return db_comm.add_recurrence(recurrence)

@app.route('/recurrence/<string:recurrence_id>/<string:category>/<string:amount>/<string:amount_frequency>/<string:description>/<string:start_date>/<string:end_date>/<string:type>/<string:repeat_start_date>/<string:days_till_repeat>', methods=['PUT'])
def update_recurrence(recurrence_id, category, amount, amount_frequency, description, start_date, end_date,type, repeat_start_date, days_till_repeat):
    print("[api] update_recurrence()")

    description = None if description == "null" else description
    repeat_start_date = None if is_valid_or_none(repeat_start_date) is None else string_to_date(repeat_start_date)
    description = None if is_valid_or_none(description) is None else description
    tp = RecurrenceType.EXPENSE if type == 2 else RecurrenceType.INCOME

    recurrence = Recurrence(category=category, amount=amount, amount_frequency=amount_frequency, start_date=start_date, end_date=end_date, description=description, recurrence_id=recurrence_id, type=tp, repeat_start_date=repeat_start_date, days_till_repeat=days_till_repeat)
    return db_comm.update_recurrence(recurrence)

@app.route('/recurrence/<string:recurrence_id>', methods=['DELETE'])
def delete_recurrence(recurrence_id):
    print("[api] delete_recurrence()")

    return db_comm.delete_recurrence(recurrence_id)

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
