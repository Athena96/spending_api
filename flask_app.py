from datetime import datetime

from flask import Flask, jsonify, render_template
from flask import current_app

from db_comms import DBCommms
from models import Recurrence
from models import SummaryPageInfo
from models import Transaction
from timeline_generator import TimelineGenerator
from utilities import outside_to_python_recurrence
from utilities import outside_to_python_transaction
from utilities import string_to_date

# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = ""
ENVIRONMENT = ""
db_comm = None
with app.app_context():
    file = current_app.open_resource('app.properties')
    text = str(file.read().decode("utf-8"))
    parts = text.split("\n")
    DATABASE = parts[0].split("=")[1]
    MONTHS_GENERATED = int(parts[1].split("=")[1])
    GREEN_RANGE = float(parts[2].split("=")[1])
    YELLOW_RANGE = float(parts[3].split("=")[1])

    print("DATABASE: ", DATABASE)
    print("MONTHS_GENERATED: ", MONTHS_GENERATED)
    print("GREEN_RANGE: ", GREEN_RANGE)
    print("YELLOW_RANGE: ", YELLOW_RANGE)

    db_comm = DBCommms(DATABASE)
    if "inherentVice" in DATABASE:
        ENVIRONMENT = "http://inherentvice.pythonanywhere.com"
    else:
        ENVIRONMENT = "http://127.0.0.1:5000"


# Website page handlers: Summary

@app.route("/site/summary", methods=["GET"])
def summary_root_page():
    print("summary_root_page()")

    summary_links = get_date_page_links("summary")
    return render_template('root_summary.html', summary_links=summary_links, prefix=ENVIRONMENT)


@app.route("/site/summary/year:<string:year>/month:<string:month>", methods=["GET"])
def summary_page(year, month):
    print("summary_page()")
    (year_income, month_income) = db_comm.get_income(year, month)
    (spent_in_year_str, spent_in_month_str) = db_comm.get_spending(year, month)

    aggregations = []
    aggregate_map = db_comm.get_transaction_aggregations(year=year, month=month)
    for category in aggregate_map.keys():
        aggregations.append(SummaryPageInfo(category=category, spent_so_far_month=aggregate_map[category][0], spent_so_far_year=aggregate_map[category][1]))

    sorted_aggregations = sorted(aggregations, key=lambda x: x.spent_so_far_month, reverse=True)
    return render_template('summary.html',
                           aggregations=sorted_aggregations,
                           month=month, year=year,
                           spent_in_month=spent_in_month_str, spent_in_year=spent_in_year_str,
                           month_income=month_income, year_income=year_income, prefix=ENVIRONMENT)

# Website page handlers: Timeline

@app.route("/site/timeline", methods=["GET"])
def timeline_page():
    print("timeline_page()")
    STARTING_BAL = db_comm.get_starting_bal()
    recurrences = db_comm.get_recurrences(None)
    generator = TimelineGenerator(months_to_generate=MONTHS_GENERATED, db_comm=db_comm, initial_recurrences=recurrences,
                                  starting_balance=STARTING_BAL, green_range=GREEN_RANGE, yellow_range=YELLOW_RANGE)
    table = generator.generate_table()

    last_day_bal_num = round(table[len(table) - 1].balance, 2)
    last_day_bal = "${}".format(last_day_bal_num)
    last_day_bal_dff = "${}".format(round((last_day_bal_num - GREEN_RANGE), 2))
    return render_template('timeline.html', timeline_table=table, last_day_bal=last_day_bal,
                           last_day_bal_dff=last_day_bal_dff,
                           greens=generator.green,
                           yellows=generator.yellow,
                           reds=generator.red,
                           STARTING_BAL=STARTING_BAL,
                           prefix=ENVIRONMENT)


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
    return render_template('add_transaction.html', transaction=transaction, prefix=ENVIRONMENT)


@app.route("/site/transactions/year:<string:year>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/category:<string:category>", methods=["GET"])
@app.route("/site/transactions/year:<string:year>/month:<string:month>/category:<string:category>", methods=["GET"])
@app.route("/site/transactions/start_date:<string:start_date>/end_date:<string:end_date>/category:<string:category>",
           methods=["GET"])
def transactions_page(year=None, month=None, category="ALL", start_date=None, end_date=None):
    print("transactions_page()")

    # if displaying only transactions between certain period
    if start_date is not None and end_date is not None:
        sd = string_to_date(start_date)
        ed = string_to_date(end_date)

        # get transactions for period recurrence
        period_recurrence_period_transactions = db_comm.get_transactions_between(start_date=sd, end_date=ed,
                                                                                 category=category)

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
    transactions = sorted(year_transactions if month is None else month_transactions, key=lambda x: x.date,
                          reverse=True)

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
                           txn_date_map_keys=sorted(txn_date_map.keys(), reverse=True),
                           txn_date_map=txn_date_map,
                           spent_in_month=spent_in_month_str, spent_in_year=spent_in_year_str,
                           month_income=month_income, year_income=year_income, prefix=ENVIRONMENT)


# Website page handlers: Recurrence

@app.route("/site/add_recurrence", methods=["GET"])
@app.route("/site/add_recurrence/<string:recurrence_id>", methods=["GET"])
def add_recurrence_page(recurrence_id=None):
    print("add_recurrence_page()")

    recurrence = db_comm.get_recurrence(recurrence_id)
    return render_template('add_recurrence.html', recurrence=recurrence, prefix=ENVIRONMENT)


@app.route("/site/recurrences", methods=["GET"])
def recurrence_page():
    print("recurrences_page()")
    recurrences = db_comm.get_recurrences(None)
    return render_template('recurrences.html', recurrences=recurrences, prefix=ENVIRONMENT)


# Transaction API endpoints

@app.route('/transactions/<string:year>', methods=['GET'])
@app.route('/transactions/<string:year>/<string:month>/<string:category>', methods=['GET'])
def get_transactions(year=None, month=None, category="ALL"):
    print("[api] get_transactions()")

    return jsonify([transaction.to_dict() for transaction in db_comm.get_transactions(year, month, category)])


@app.route(
    '/transactions/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>/<string:var_txn_tracking>/<string:txn_type>',
    methods=['POST'])
def add_transaction(title, amount, category, date, description, var_txn_tracking, txn_type):
    print("[api] add_transaction()")

    transaction = outside_to_python_transaction(title=title, amount=amount, category=category, date=date,
                                               description=description, var_txn_tracking=var_txn_tracking,
                                               txn_type=txn_type)
    return db_comm.add_transaction(transaction)


@app.route(
    '/transactions/<string:transaction_id>/<string:title>/<string:amount>/<string:category>/<string:date>/<string:description>/<string:var_txn_tracking>/<string:txn_type>',
    methods=['PUT'])
def update_transaction(transaction_id, title, amount, category, date, description, var_txn_tracking, txn_type):
    print("[api] update_transaction()")

    transaction = outside_to_python_transaction(title=title, amount=amount, category=category, date=date,
                                               description=description, var_txn_tracking=var_txn_tracking,
                                               txn_type=txn_type, transaction_id=transaction_id)
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


@app.route(
    '/recurrence/<string:name>/<string:amount>/<string:description>/<string:rec_type>/<string:start_date>/<string:end_date>/<string:days_till_repeat>/<string:day_of_month>',
    methods=['POST'])
def add_recurrence(name, amount, description, rec_type, start_date, end_date, days_till_repeat, day_of_month):
    print("[api] add_recurrence()")

    recurrence = outside_to_python_recurrence(name=name, amount=amount, description=description, rec_type=rec_type,
                                              start_date=start_date, end_date=end_date,
                                              days_till_repeat=days_till_repeat, day_of_month=day_of_month)
    return db_comm.add_recurrence(recurrence)


@app.route(
    '/recurrence/<string:recurrence_id>/<string:name>/<string:amount>/<string:description>/<string:rec_type>/<string:start_date>/<string:end_date>/<string:days_till_repeat>/<string:day_of_month>',
    methods=['PUT'])
def update_recurrence(recurrence_id, name, amount, description, rec_type, start_date, end_date, days_till_repeat,
                      day_of_month):
    print("[api] update_recurrence()")

    recurrence = outside_to_python_recurrence(name=name, amount=amount, description=description, rec_type=rec_type,
                                              start_date=start_date, end_date=end_date,
                                              days_till_repeat=days_till_repeat, day_of_month=day_of_month,
                                              recurrence_id=recurrence_id)
    return db_comm.update_recurrence(recurrence)


@app.route('/recurrence/<string:recurrence_id>', methods=['DELETE'])
def delete_recurrence(recurrence_id):
    print("[api] delete_recurrence()")

    return db_comm.delete_recurrence(recurrence_id)


@app.route('/timeline/<string:starting_bal>', methods=['POST'])
def set_starting_bal(starting_bal):
    print("[api] set_starting_bal()")

    return db_comm.set_starting_bal(starting_bal)



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

    return ((obj[0], (sorted(obj[1], reverse=True))) for obj in sorted(final_year_links, reverse=True))
