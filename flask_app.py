from flask import Flask, jsonify, request, render_template
from db_comms import DBCommms
from datetime import datetime
import sqlite3


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

@app.route("/site/purchases", methods=["GET"])
@app.route("/site/purchases/<string:month>/<string:year>/<string:category>", methods=["GET"])
def purchases_page(month=None, year=None, category="ALL"):
    if month == None and year == None:
        (month,year) = get_current_date()

    pay = get_income_data()

    month_purchases = db_comm.get_list_purchases(month, year, category)
    spent_in_month = sum([purchase.price for purchase in month_purchases])
    spent_in_month_str = str(round(spent_in_month, 2))

    year_purchases = db_comm.get_list_purchases(year=year)
    spent_in_year = sum([purchase.price for purchase in year_purchases])
    spent_in_year_str = str(round(spent_in_year, 2))

    # sort purchases, before display
    month_purchases = sorted(month_purchases, key=lambda x: x.date, reverse=True)

    return render_template('purchases.html',
    month=month,
    year=year,
    category=category,
    purchases=month_purchases,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_limit=pay["month"],
    year_limit=pay["year"])


# website page controllers for charts

@app.route("/site/chart", methods=["GET"])
def chart_page():
    return render_template('chart.html')


# website page controllers for budget

@app.route("/site/budgets", methods=["GET"])
@app.route("/site/budgets/<string:month>/<string:year>", methods=["GET"])
def budgets_page(month=None, year=None):
    if month == None and year == None:
        (month,year) = get_current_date()

    pay = get_income_data()
    budgets = db_comm.get_list_budgets()
    year_purchases = db_comm.get_list_purchases(year=year)

    budget_data = []
    for budget in budgets:
        purchases = filter(lambda purchase: (purchase.category == budget.category), year_purchases)
        if budget.amount_frequency == "month":
            purchases = filter(lambda purchase: (month ==  "{}{}".format(purchase.date[5], purchase.date[6])), purchases)

        spent_so_far = sum([purchase.price for purchase in purchases])
        spent_so_far_str = "${}".format(round(spent_so_far, 2))

        percent = "{}%".format(round(((spent_so_far / budget.amount) * 100),2))
        remaining = round((budget.amount - spent_so_far),2)
        entry = (budget.budget_id, budget.category, spent_so_far_str, percent, budget.amount, budget.amount_frequency, remaining)
        budget_data.append(entry)


    # separate into month and year
    month_budgets = filter(lambda x: x[5] == "month", budget_data)
    month_budgets = sorted(month_budgets, key=lambda x: x[4])

    year_budgets = filter(lambda x: x[5] == "year", budget_data)
    year_budgets = sorted(year_budgets, key=lambda x: x[4])

    # calc spent data
    month_purchases = db_comm.get_list_purchases(month, year, 'ALL')
    spent_in_month = sum([purchase.price for purchase in month_purchases])
    spent_in_month_str = str(round(spent_in_month, 2))

    spent_in_year = sum([purchase.price for purchase in year_purchases])
    spent_in_year_str = str(round(spent_in_year, 2))


    return render_template('budgets.html',
    month_budgets=month_budgets,
    year_budgets=year_budgets,
    month=month, year=year,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_limit=pay["month"],
    year_limit=pay["year"])

@app.route("/site/add_budget", methods=["GET"])
@app.route("/site/add_budget/<string:budget_id>", methods=["GET"])
def add_budget_page(budget_id=None):
    budget = db_comm.get_a_budget(budget_id)
    return render_template('add_budget.html', budget=budget)


# income API endpoints

@app.route("/year_income", methods=["GET"])
def get_income():
    return jsonify(get_income_data())

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

# helpers
def get_income_data():
    data = {}
    per_month_school = (280.0 + 211.0)
    total_per_year = (1930.00 * 26.0) + (per_month_school * 12.0)
    data["year"] = round(total_per_year, 2)
    data["month"] = round((total_per_year / 12.0), 2)
    return data

def get_current_date():
    year = "{}".format(datetime.now().year)
    curr_month = datetime.now().month
    month = ""
    if curr_month < 10:
        month = "0{}".format(curr_month)
    else:
        month = "{}".format(curr_month)

    return (month,year)



