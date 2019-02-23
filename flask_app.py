from flask import Flask, jsonify, request, render_template
from db_comms import DBCommms
from datetime import datetime
import os

from matplotlib.pyplot import figure
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
db_comm = DBCommms(DATABASE)


# website page controllers for purchase

@app.route("/site/add_purchase", methods=["GET"])
@app.route("/site/add_purchase/<string:purchase_id>", methods=["GET"])
def add_purchase_page(purchase_id=None):
    print("add_purchase_page()")
    purchase = db_comm.get_purchase(purchase_id)
    return render_template('add_purchase.html', purchase=purchase)

@app.route("/site/purchases", methods=["GET"])
@app.route("/site/purchases/<string:month>/<string:year>/<string:category>", methods=["GET"])
def purchases_page(month=None, year=None, category="ALL"):
    print("purchases_page()")
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

    if month == "ALL" and year != None:
        print("YEAR ONLY PURCHASES~")
        year_purchases = db_comm.get_list_purchases(year=year, category=category)

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


# website page controllers for charts

@app.route("/site/chart", methods=["GET"])
@app.route("/site/chart/<string:month>/<string:year>", methods=["GET"])
def chart_page(month=None, year=None):
    print("chart_page()")

    # get current month and year
    if month == None and year == None:
        (m,y) = get_current_date()
        month = m
        year = y

    ## check if i need to generate new graphs
    # get ID of most recent purchase
    current_max_purchaseID = str(db_comm.cursor.execute("select max(spending.purchase_id) from spending").fetchone()[0])
    # get ID of previously generated graph
    mydir = '/home/inherentVice/mysite/static/images/'
    files = os.listdir(mydir)
    if len(files) > 0:
        aFile = files[0]
        name_parts = aFile.split("_")
        if (len(name_parts) == 4):
            previous_max_purchaseID_name = name_parts[len(name_parts)-1]
            previous_max_purchaseID = previous_max_purchaseID_name.split(".")[0]
            # if the purchase ID's match, no need to generate new graph
            if previous_max_purchaseID == current_max_purchaseID:
                return render_template('chart.html', year=year, month=month, curr_version=current_max_purchaseID)

    ## Need to generate New graph

    # delete previous graph images
    filelist = [ f for f in os.listdir(mydir) ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))

    # get all budget categories
    db_comm.cursor.execute(
    '''
    select budget.category, budget.amount, budget.amount_frequency
    from budget
    ''')

    # create month and year spending dictionaries
    month_spending = {}
    year_spending = {}
    for budget_category in db_comm.cursor.fetchall():
        category = (budget_category[0].encode('ascii','ignore')).decode('UTF-8')
        amount = float(budget_category[1])
        amount_frequency = (budget_category[2].encode('ascii','ignore')).decode('UTF-8')
        if amount_frequency == "month":
            month_spending[category] = (0.0, float(amount))
        elif amount_frequency == "year":
            year_spending[category] = (0.0, float(amount))

    # fretch, match, and save all purchase data
    q = """select sum(spending.price), spending.category from spending where spending.date like('{0}-{1}%') and spending.category not in (select budget.category from budget where budget.amount_frequency = 'year') group by spending.category """.format(year, month)
    db_comm.cursor.execute(q)

    for month_purchase_aggregate in db_comm.cursor.fetchall():
        category = (month_purchase_aggregate[1].encode('ascii','ignore')).decode('UTF-8')
        spent = float(month_purchase_aggregate[0])
        month_spending[category] = (spent, month_spending[category][1])


    db_comm.cursor.execute(
        """
        select sum(spending.price), spending.category
        from spending
        where spending.date like('{0}-%')
            and spending.category in (select budget.category from budget where budget.amount_frequency = 'year')
        group by spending.category
        """.format(year))
    for year_purchase_aggregate in db_comm.cursor.fetchall():
        category = (year_purchase_aggregate[1].encode('ascii','ignore')).decode('UTF-8')
        spent = float(year_purchase_aggregate[0])
        year_spending[category] = (spent, year_spending[category][1])

    # sort the data by budget.amount
    month_spending_categories = sorted(month_spending.keys(), key=lambda x: month_spending[x][1])
    month_spending_planned = [int(month_spending[category][1]) for category in month_spending_categories]
    month_spending_actual = [int(month_spending[category][0]) for category in month_spending_categories]

    year_spending_categories = sorted(year_spending.keys(), key=lambda x: year_spending[x][1])
    year_spending_planned = [int(year_spending[category][1]) for category in year_spending_categories]
    year_spending_actual = [int(year_spending[category][0]) for category in year_spending_categories]


    ## Plot the data
    # data to plot
    n_groups_month = len(month_spending)
    n_groups_year = len(year_spending)

    # create MONTH plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups_month)
    bar_width = 0.50
    opacity = 0.8

    rects1 = plt.bar(index, month_spending_actual, bar_width * 0.75, alpha=opacity, color='b', label='Actual')
    rects2 = plt.bar(index + (bar_width), month_spending_planned, bar_width * 0.75,  alpha=opacity, color='g', label='Planned')
    for rect in rects1 + rects2:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, '$%d ' % int(height), ha='center', va='bottom')

    plt.xlabel('Categories')
    plt.xticks(rotation=90)
    plt.ylabel('Spending')
    plt.title('Month Categorical Spending')
    plt.xticks(index + (bar_width/2), month_spending_categories)
    plt.legend()

    # write the file
    outputFileName = '/home/inherentVice/mysite/static/images/{}-{}_month_plot_{}.png'.format(year, month, current_max_purchaseID)
    DefaultSize = plt.gcf().get_size_inches()
    plt.gcf().set_size_inches( (DefaultSize[0]*2.75, DefaultSize[1]*2.75) )
    plt.savefig(outputFileName, dpi=300)
    fileExists = False
    while fileExists == False:
        if os.path.isfile(outputFileName):
            fileExists = True


    # create YEAR plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups_year)
    bar_width = 0.50
    opacity = 0.8

    rects1 = plt.bar(index, year_spending_actual, bar_width * 0.75, alpha=opacity, color='b', label='Actual')
    rects2 = plt.bar(index + bar_width , year_spending_planned, bar_width * 0.75,  alpha=opacity, color='g', label='Planned')
    for rect in rects1 + rects2:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2.0, height, '$%d ' % int(height), ha='center', va='bottom')

    plt.xlabel('Categories')
    plt.xticks(rotation=90)
    plt.ylabel('Spending')
    plt.title('Year Categorical Spending')
    plt.xticks(index + (bar_width/2), year_spending_categories)
    plt.legend()

    # write the file
    outputFileName = '/home/inherentVice/mysite/static/images/{}-{}_year_plot_{}.png'.format(year, month, current_max_purchaseID)
    DefaultSize = plt.gcf().get_size_inches()
    plt.gcf().set_size_inches( (DefaultSize[0]*2.75, DefaultSize[1]*2.75) )
    plt.savefig(outputFileName, dpi=300)
    fileExists = False
    while fileExists == False:
        if os.path.isfile(outputFileName):
            fileExists = True
    # 4. pass date to html page
    return render_template('chart.html', year=year, month=month, curr_version=current_max_purchaseID)


# website page controllers for budget

@app.route("/site/budgets", methods=["GET"])
@app.route("/site/budgets/<string:month>/<string:year>", methods=["GET"])
def budgets_page(month=None, year=None):
    print("budgets_page()")
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
    print("add_budget_page()")
    budget = db_comm.get_a_budget(budget_id)
    return render_template('add_budget.html', budget=budget)


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
    result = db_comm.get_purchases(month,year,category)
    return result

@app.route('/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['POST'])
def add_purchase(item, price, category, date, note):
    print("add_purchase()")
    result = db_comm.add_purchase(item, price, category, date, note)
    return result

@app.route('/<string:purchase_id>/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['PUT'])
def update_purchase(purchase_id, item, price, category, date, note):
    print("update_purchase()")
    result = db_comm.update_purchase(purchase_id, item, price, category, date, note)
    return result

@app.route('/<string:purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    print("delete_purchase()")
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
    result = db_comm.add_budget_category(category, amount, amount_frequency)
    return result


@app.route('/budget/<string:category_id>/<string:category>/<string:amount>/<string:amount_frequency>', methods=['PUT'])
def update_budget_category(category_id, category, amount, amount_frequency):
    print("update_budget_category()")
    result = db_comm.update_budget_category(category_id, category, amount, amount_frequency)
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
    per_month_school = (280.0 + 211.0)
    total_per_year = (1930.00 * 26.0) + (per_month_school * 12.0)
    data["year"] = round(total_per_year, 2)
    data["month"] = round((total_per_year / 12.0), 2)
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



