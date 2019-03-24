from flask import Flask, jsonify, render_template
from db_comms import DBCommms
from datetime import datetime
from models import Purchase
from models import Budget
from datetime import timedelta

# declare our Flask app
app = Flask(__name__)


# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
db_comm = DBCommms(DATABASE)


## Website page handlers

# website page controllers for purchase

@app.route("/site/add_purchase", methods=["GET"])
@app.route("/site/add_purchase/<string:purchase_id>", methods=["GET"])
def add_purchase_page(purchase_id=None):
    print("add_purchase_page()")
    purchase = db_comm.get_purchase(purchase_id)
    budgets = db_comm.get_budgets()
    return render_template('add_purchase.html', purchase=purchase, budgets=budgets)

@app.route("/site/purchases", methods=["GET"])
@app.route("/site/purchases/<string:month>/<string:year>/<string:category>", methods=["GET"])
def purchases_page(month=None, year=None, category="ALL"):
    print("purchases_page()")
    if month == None and year == None:
        (month,year) = get_current_date()

    pay = get_income_data()

    month_purchases = db_comm.get_purchases(month, year, category)
    spent_in_month = sum([purchase.price for purchase in month_purchases])
    spent_in_month_str = str(round(spent_in_month, 2))

    year_purchases = db_comm.get_purchases(year=year)
    spent_in_year = sum([purchase.price for purchase in year_purchases])
    spent_in_year_str = str(round(spent_in_year, 2))

    # sort purchases, before display
    month_purchases = sorted(month_purchases, key=lambda x: x.date, reverse=True)

    if month == "ALL" and year != None:
        year_purchases = db_comm.get_purchases(year=year, category=category)

        return render_template('purchases.html',
        month="--",
        year=year,
        category=category,
        purchases=year_purchases,
        spent_in_month=spent_in_month_str,
        spent_in_year=spent_in_year_str,
        month_limit=pay["month"],
        year_limit=pay["year"])

    return render_template('purchases.html',
    month=month,
    year=year,
    category=category,
    purchases=month_purchases,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_limit=pay["month"],
    year_limit=pay["year"])

# website page controllers for budget

@app.route("/site/budgets", methods=["GET"])
@app.route("/site/budgets/<string:month>/<string:year>", methods=["GET"])
def budgets_page(month=None, year=None):
    # TODO SIMPLIFY
    print("budgets_page()")
    if month == None and year == None:
        (page_month,page_year) = get_current_date()
        print((page_month,page_year))

    pay = get_income_data()
    budgets = db_comm.get_budgets()
    year_purchases = db_comm.get_purchases(year=page_year)

    budget_data = []
    for budget in budgets:
        purchases = filter(lambda purchase: (purchase.category == budget.category), year_purchases)
        if budget.amount_frequency == "month":
            purchases = filter(lambda purchase: (page_month ==  "{}{}".format(purchase.date[5], purchase.date[6])), purchases)

        if "special" in budget.amount_frequency:
            (year, month, day) = budget.get_startdate()
            duration_days = budget.get_duration()
            start_date = datetime(year=year, month=month, day=day)
            end_date = start_date + timedelta(days=duration_days)

            cmd = """select sum(spending.price) from spending where spending.category = '{0}' and spending.date >= '{1}-{2}-{3} 00:00:00' and spending.date <= '{4}-{5}-{6} 23:59:59'""".format(budget.category, year, '{:02d}'.format(month), '{:02d}'.format(day), end_date.year, '{:02d}'.format(end_date.month), '{:02d}'.format(end_date.day))
            print(cmd)
            print(db_comm.cursor.execute(cmd))

            spent_so_far = db_comm.cursor.fetchone()[0]
            if spent_so_far is None:
                spent_so_far = 0.0

            spent_so_far_str = "{}".format(round(spent_so_far, 2))

            p = (spent_so_far / budget.amount)
            percent = ""
            if p >= 0.0 and p < 0.9:
                percent = "green"
            elif p >= 0.9 and p < 0.99:
                percent = "orange"
            elif p >= 0.99 and p <= 1.00:
                percent = "blue"
            else:
                percent = "red"
            remaining = round((budget.amount - spent_so_far),2)
            entry = (budget.budget_id, budget.category, spent_so_far_str, percent, budget.amount, budget.amount_frequency, remaining)
            budget_data.append(entry)
            continue


        spent_so_far = sum([purchase.price for purchase in purchases])
        spent_so_far_str = "{}".format(round(spent_so_far, 2))

        p = (spent_so_far / budget.amount)
        percent = ""
        if p >= 0.0 and p < 0.9:
            percent = "green"
        elif p >= 0.9 and p < 0.99:
            percent = "orange"
        elif p >= 0.99 and p <= 1.00:
            percent = "blue"
        else:
            percent = "red"
        remaining = round((budget.amount - spent_so_far),2)
        entry = (budget.budget_id, budget.category, spent_so_far_str, percent, budget.amount, budget.amount_frequency, remaining)
        budget_data.append(entry)

    # separate into month and year
    month_budgets = filter(lambda x: x[5] == "month", budget_data)
    month_budgets = sorted(month_budgets, key=lambda x: x[4])

    year_budgets = filter(lambda x: x[5] == "year", budget_data)
    year_budgets = sorted(year_budgets, key=lambda x: x[4])

    special_budgets = filter(lambda x: ("special" in x[5]), budget_data)
    special_budgets = sorted(special_budgets, key=lambda x: x[4])

    # calc spent data
    month_purchases = db_comm.get_purchases(page_month, page_year, 'ALL')
    spent_in_month = sum([purchase.price for purchase in month_purchases])
    spent_in_month_str = str(round(spent_in_month, 2))

    spent_in_year = sum([purchase.price for purchase in year_purchases])
    spent_in_year_str = str(round(spent_in_year, 2))

    return render_template('budgets.html',
    month_budgets=month_budgets,
    year_budgets=year_budgets,
    special_budgets=special_budgets,
    month=page_month, year=page_year,
    spent_in_month=spent_in_month_str,
    spent_in_year=spent_in_year_str,
    month_limit=pay["month"],
    year_limit=pay["year"])

@app.route("/site/add_budget", methods=["GET"])
@app.route("/site/add_budget/<string:budget_id>", methods=["GET"])
def add_budget_page(budget_id=None):
    print("add_budget_page()")
    budget = db_comm.get_budget(budget_id)
    return render_template('add_budget.html', budget=budget)


## API handlers

# income API endpoints

@app.route("/year_income", methods=["GET"])
def get_income():
    print("get_income()")
    return jsonify(get_income_data())

# purchase API endpoints

@app.route('/<string:year>', methods=['GET'])
@app.route('/<string:month>/<string:year>/<string:category>', methods=['GET']) #TODO change order year/month
def get_all_purchases_for_year(month=None, year=None, category="ALL"):
    print("get_all_purchases_for_year()")
    result = to_json(db_comm.get_purchases(month,year,category))
    return result

@app.route('/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['POST'])
def add_purchase(item, price, category, date, note):
    print("add_purchase()")
    purchase = Purchase(item, price, category, date, note)
    result = db_comm.add_purchase(purchase)
    return result

@app.route('/<string:purchase_id>/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['PUT'])
def update_purchase(purchase_id, item, price, category, date, note):
    print("update_purchase()")
    purchase = Purchase(item, price, category, date, note, purchase_id)
    result = db_comm.update_purchase(purchase)
    return result

@app.route('/<string:purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    print("delete_purchase()")
    result = db_comm.delete_purchase(purchase_id)
    return result

# budget API endpoints

@app.route('/budgets', methods=['GET'])
def get_budgets():
    print("get_budgets()")
    result = to_json(db_comm.get_budgets())
    return result

@app.route('/budget/<string:category>/<string:amount>/<string:amount_frequency>', methods=['POST'])
def add_budget_category(category, amount, amount_frequency):
    print("add_budget_category()")
    budget = Budget(category, amount, amount_frequency)
    result = db_comm.add_budget_category(budget)
    return result

@app.route('/budget/<string:category_id>/<string:category>/<string:amount>/<string:amount_frequency>', methods=['PUT'])
def update_budget_category(category_id, category, amount, amount_frequency):
    print("update_budget_category()")
    budget = Budget(category, amount, amount_frequency, category_id)
    result = db_comm.update_budget_category(budget)
    return result

@app.route('/budget/<string:category_id>', methods=['DELETE'])
def delete_budget_category(category_id):
    print("delete_budget_category()")
    result = db_comm.delete_budget_category(category_id)
    return result


# helpers
def get_income_data():
    print("Helper: get_income_data()")
    data = {}

    query = "select year from income"
    db_comm.cursor.execute(query)
    data["year"] = db_comm.cursor.fetchone()[0]

    query = "select month from income"
    db_comm.cursor.execute(query)
    data["month"] = db_comm.cursor.fetchone()[0]
    print(data)

    return data

def get_current_date():
    print("Helper: get_current_date()")
    year = "{}".format(datetime.now().year)
    curr_month = datetime.now().month
    month = ""
    if curr_month < 10:
        month = "0{}".format(curr_month)
    else:
        month = "{}".format(curr_month)

    return (month,year)

def to_json(data):
    json_data = []
    for element in data:
        json_data.append(element.to_dict())
    return jsonify(json_data)

