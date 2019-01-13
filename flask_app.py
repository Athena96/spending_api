from flask import Flask, jsonify, request, render_template
import sqlite3
from db_comms import DBCommms


# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
db_comm = DBCommms(DATABASE)

@app.route("/site/add_purchase", methods=["GET"])
def add_purchase_page():
    return render_template('add_purchase.html')

@app.route("/site/purchases/<string:month>/<string:year>/<string:category>", methods=["GET"])
def purchases_page(month, year, category):
    month_purchase_tuples = db_comm.get_list_purchases(month, year, category)

    # total monthly spending
    spent_in_month = 0.0
    for p in month_purchase_tuples:
        spent_in_month += p[2]

    # total yearly spending
    spent_in_year = 0.0
    year_purchase_tuples = db_comm.get_list_purchases(year=year)
    for p in year_purchase_tuples:
        spent_in_year += p[2]

    # total monthly limit
    month_limit = 0.0
    budget_tuples = db_comm.get_list_budgets()
    for b in budget_tuples:
        if b[2] == "month":
            month_limit += b[1]
        elif b[2] == "year":
            month_limit += (b[1] / 12.0)
        else:
            month_limit += (b[1] / (4.0 * 12.0))

    month_limit_str = str(round(month_limit, 2))

    # total yearly limit
    year_limit = month_limit * 12.0

    return render_template('purchases.html', month=month, year=year, category=category,purchases=month_purchase_tuples,spent_in_month=spent_in_month,spent_in_year=spent_in_year,
        month_limit=month_limit_str,year_limit=year_limit)

@app.route("/site/budgets", methods=["GET"])
def budgets_page():
    budget_tuples = db_comm.get_list_budgets()
    return render_template('budgets.html', budgets=budget_tuples)

# Purchases Table Endpoints

@app.route('/<string:year>', methods=['GET'])
def get_all_purchases_for_year(year):
    print("get_all_purchases_for_year()")
    result = db_comm.get_purchases(year=year)
    return result

@app.route('/<string:month>/<string:year>/<string:category>', methods=['GET'])
def get_all_purchases(month, year, category):
    print("get_all_purchases()")
    result = db_comm.get_purchases(month,year,category)
    return result


@app.route('/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['POST'])
def add_purchase(item, price, category, date, note):
    print("add_purchase()")
    print((item, price, category, date, note))
    result = db_comm.add_purchase(item, price, category, date, note)
    return result


@app.route('/<string:purchase_id>/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['PUT'])
def update_purchase(purchase_id, item, price, category, date, note):
    print("update_purchase()")
    print((item, price, category, date, note))
    result = db_comm.update_purchase(purchase_id, item, price, category, date, note)
    return result


@app.route('/<string:purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    print("delete_purchase()")
    print(purchase_id)
    result = db_comm.delete_purchase(purchase_id)
    return result


@app.route('/<string:month>/<string:year>', methods=['GET'])
def get_spending_report(month, year):
    print("get_spending_report")
    print((month, year))
    result = db_comm.get_spending_report(month, year)
    return result

# Budget Table Endpoints

@app.route('/budget', methods=['GET'])
def get_budget():
    print("get_budget()")
    result = db_comm.get_budget()
    return result

@app.route('/budget/<string:category>/<string:amount>/<string:amount_frequency>', methods=['POST'])
def add_budget_category(category, amount, amount_frequency):
    print("add_budget_category()")
    print((category, amount, amount_frequency))
    result = db_comm.add_budget_category(category, amount, amount_frequency)
    return result


@app.route('/budget/<string:category_id>/<string:category>/<string:amount>/<string:amount_frequency>', methods=['PUT'])
def update_budget_category(category_id, category, amount, amount_frequency):
    print("update_budget_category()")
    print((category_id, category, amount, amount_frequency))
    result = db_comm.update_budget_category(category_id, category, amount, amount_frequency)
    return result


@app.route('/budget/<string:category_id>', methods=['DELETE'])
def delete_budget_category(category_id):
    print("delete_budget_category()")
    print(category_id)
    result = db_comm.delete_budget_category(category_id)
    return result

