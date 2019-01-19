from flask import Flask, jsonify, request, render_template
import sqlite3
from db_comms import DBCommms


# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
db_comm = DBCommms(DATABASE)


# website page controllers for purchase

@app.route("/site/add_purchase", methods=["GET"])
@app.route("/site/add_purchase/<string:purchase_id>", methods=["GET"])
def add_purchase_page(purchase_id=None):
    purchase = db_comm.get_purchase(purchase_id)
    return render_template('add_purchase.html', purchase=purchase)

@app.route("/site/purchases/<string:month>/<string:year>/<string:category>", methods=["GET"])
def purchases_page(month, year, category):
    month_purchases = db_comm.get_list_purchases(month, year, category)
    month_purchases = sorted(month_purchases, key=lambda x: x.date, reverse=True)

    # total monthly spending
    spent_in_month = 0.0
    for purchase in month_purchases:
        spent_in_month += purchase.price

    spent_in_month_str = str(round(spent_in_month, 2))

    # total yearly spending
    spent_in_year = 0.0
    year_purchases = db_comm.get_list_purchases(year=year)
    for purchase in year_purchases:
        spent_in_year += purchase.price

    spent_in_year_str = str(round(spent_in_year, 2))

    # total monthly limit
    month_limit = 0.0
    budgets = db_comm.get_list_budgets()
    for budget in budgets:
        if budget.amount_frequency == "month":
            month_limit += budget.amount
        elif budget.amount_frequency == "year":
            month_limit += (budget.amount / 12.0)
        else:
            month_limit += (budget.amount / (4.0 * 12.0))

    month_limit_str = str(round(month_limit, 2))

    # total yearly limit
    year_limit = month_limit * 12.0
    year_limit_str = str(round(year_limit, 2))

    return render_template('purchases.html',
    month=month,
    year=year,
    category=category,
    purchases=month_purchases,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_limit=month_limit_str,
    year_limit=year_limit_str)


# website page controllers for charts

@app.route("/site/chart", methods=["GET"])
def chart_page():
    return render_template('chart.html')


# website page controllers for budget

@app.route("/site/budgets/<string:month>/<string:year>", methods=["GET"])
def budgets_page(month, year):
    budgets = db_comm.get_list_budgets()
    year_purchases = db_comm.get_list_purchases(year=year)

    budget_data = []
    for budget in budgets:
        spent_so_far = 0.0
        for purchase in year_purchases:
            # 2019-01-01 16:23:00
            curr_month = "{}{}".format(purchase.date[5], purchase.date[6])

            if purchase.category == budget.category and budget.amount_frequency == "month" and month == curr_month:
                spent_so_far += purchase.price
            elif purchase.category == budget.category and budget.amount_frequency == "year":
                spent_so_far += purchase.price


        spent_so_far_str = "${}".format(round(spent_so_far, 2))

        percent = "{}%".format(round(((spent_so_far / budget.amount) * 100),2))
        entry = (budget.budget_id, budget.category, spent_so_far_str, percent, budget.amount, budget.amount_frequency)
        budget_data.append(entry)


    # separate into month and year
    month_budgets = filter(lambda x: x[5] == "month", budget_data)
    month_budgets = sorted(month_budgets, key=lambda x: x[4])

    year_budgets = filter(lambda x: x[5] == "year", budget_data)
    year_budgets = sorted(year_budgets, key=lambda x: x[4])

    month_purchases = db_comm.get_list_purchases(month, year, 'ALL')

    # total monthly spending
    spent_in_month = 0.0
    for purchase in month_purchases:
        spent_in_month += purchase.price

    spent_in_month_str = str(round(spent_in_month,2))

    # total yearly spending
    spent_in_year = 0.0
    year_purchases = db_comm.get_list_purchases(year=year)
    for purchase in year_purchases:
        spent_in_year += purchase.price

    spent_in_year_str = str(round(spent_in_year,2))

    # total monthly limit
    month_limit = 0.0
    budgets = db_comm.get_list_budgets()
    for budget in budgets:
        if budget.amount_frequency == "month":
            month_limit += budget.amount
        elif budget.amount_frequency == "year":
            month_limit += (budget.amount / 12.0)
        else:
            month_limit += (budget.amount / (4.0 * 12.0))

    month_limit_str = str(round(month_limit, 2))

    # total yearly limit
    year_limit = month_limit * 12.0
    year_limit_str = str(round(year_limit,2))

    return render_template('budgets.html',
    month_budgets=month_budgets,
    year_budgets=year_budgets,
    month=month, year=year,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_limit=month_limit_str,
    year_limit=year_limit_str)

@app.route("/site/add_budget", methods=["GET"])
@app.route("/site/add_budget/<string:budget_id>", methods=["GET"])
def add_budget_page(budget_id=None):
    budget = db_comm.get_a_budget(budget_id)
    return render_template('add_budget.html', budget=budget)


# purchase API endpoints

@app.route('/<string:year>', methods=['GET'])
@app.route('/<string:month>/<string:year>/<string:category>', methods=['GET']) #TODO change order year/month
def get_all_purchases_for_year(month=None, year=None, category="ALL"):
    print("get_all_purchases_for_year()")
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

# budget API endpoints

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

