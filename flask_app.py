from flask import Flask, jsonify
import sqlite3
from db_comms import DBCommms

class Purchase:

    def __init__(self, item, price, category, date, note=None):
        self.item = item
        self.price = price
        self.category = category
        self.date = date
        self.note = note


# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
#db_comm = DBCommms(DATABASE)

@app.route('/<string:year>', methods=['GET'])
def get_all_purchases_for_year(year):
    print("get_all_purchases()")
    print(year)

    # open
    db_conn = sqlite3.connect(DATABASE)
    cursor = db_conn.cursor()

    # query
    begin_date = "{0}-01-01 00:00:00".format(year)
    end_date = "{0}-12-31 00:00:00".format(year)

    cursor.execute("SELECT * FROM spending where spending.date >= '{0}' and spending.date <= '{1}'".format(begin_date, end_date))

    data = []
    for purchase_id, item, price, category, date, note in cursor:
        contents = {}
        contents["purchase_id"] = purchase_id
        contents["item"] = item
        contents["price"] = price
        contents["category"] = category
        contents["date"] = date
        contents["note"] = note
        data.append(contents)

    # close
    db_conn.close()

    # FUTURE
    #result = db_comm.get_purchases(year=2018)

    # send data
    return jsonify(data)

@app.route('/<string:month>/<string:year>/<string:category>', methods=['GET'])
def get_all_purchases(month, year, category):
    print("get_all_purchases()")
    print((month, year, category))

    # open
    db_conn = sqlite3.connect(DATABASE)
    cursor = db_conn.cursor()

    # query
    begin_date = "{0}-{1}-01 00:00:00".format(year, month)
    end_date = "{0}-{1}-31 00:00:00".format(year, month)

    if category == "ALL":
        cursor.execute("SELECT * FROM spending where spending.date >= '{0}' and spending.date <= '{1}'".format(begin_date, end_date))
    else:
        cursor.execute("SELECT * FROM spending where spending.date >= '{0}' and spending.date <= '{1}' and spending.category = '{2}'".format(begin_date, end_date, category))

    data = []
    for purchase_id, item, price, category, date, note in cursor:
        contents = {}
        contents["purchase_id"] = purchase_id
        contents["item"] = item
        contents["price"] = price
        contents["category"] = category
        contents["date"] = date
        contents["note"] = note
        data.append(contents)

    # close
    db_conn.close()

    # send data
    return jsonify(data)

@app.route('/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['POST'])
def add_purchase(item, price, category, date, note):
    print("add_purchase()")
    print((item, price, category, date, note))

    # open
    db_conn = sqlite3.connect(DATABASE)
    cursor = db_conn.cursor()

    # add purchase
    # TODO check if it exists?
    # TODO check values are valid
    if note == "--":
        cursor.execute(
        """INSERT INTO spending (item, price, category, date, note)
        VALUES ('{0}', '{1}', '{2}', '{3}', NULL)""".format(item,
        price, category, date, note))
    else:
        cursor.execute(
        """INSERT INTO spending (item, price, category, date, note)
        VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(item,
        price, category, date, note))

    db_conn.commit()

    # close
    db_conn.close()

    return jsonify({'result': 'successfuly added purchase!'})

@app.route('/<string:purchase_id>/<string:item>/<string:price>/<string:category>/<string:date>/<string:note>', methods=['PUT'])
def update_purchase(purchase_id, item, price, category, date, note):
    print("update_purchase()")
    print((purchase_id, item, price, category, date, note))

    # open
    db_conn = sqlite3.connect(DATABASE)
    cursor = db_conn.cursor()

    cursor.execute(
    """UPDATE spending SET item = '{0}', price = {1}, category = '{2}', date = '{3}', note = '{4}'
    WHERE spending.purchase_id = {5}""".format(item,
    price, category, date, note, purchase_id))

    db_conn.commit()

    # close
    db_conn.close()

    return jsonify({'result': 'successfuly updated purchase!'})



@app.route('/<string:purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    print("delete_purchase(): ", purchase_id)
    # open
    db_conn = sqlite3.connect(DATABASE)
    cursor = db_conn.cursor()

    cursor.execute("DELETE FROM spending WHERE spending.purchase_id = {0};".format(int(purchase_id)))
    db_conn.commit()

    # close
    db_conn.close()
    return jsonify({'result': 'successfuly deleted purchase!'})


@app.route('/<string:month>/<string:year>', methods=['GET'])
def get_spending_report(month, year):
    print("get_spending_report() for: Y: {0} M: {1}".format(month, year))

    # open
    db_conn = sqlite3.connect(DATABASE)
    cursor = db_conn.cursor()

    # query
    begin_date = "{0}-{1}-01 00:00:00".format(year, month)
    end_date = "{0}-{1}-31 00:00:00".format(year, month)

    # get list of categories
    categories = {}
    cursor.execute("SELECT distinct(spending.category) from spending")
    for category in cursor:
        print("->: ", category[0])
        categories[category[0]] = 0.0

    # get month and year purchase data
    cursor.execute("SELECT spending.price, spending.category FROM spending where spending.date >= '{0}' and spending.date <= '{1}'".format(begin_date, end_date))

    # aggregate
    for price, category in cursor:
        categories[category] += float(price)

    # close
    db_conn.close()

    # send data
    return jsonify(categories)

@app.route('/budget', methods=['GET'])
def get_budget():
    print("get_budget()")

    # open
    db_conn = sqlite3.connect(DATABASE)
    cursor = db_conn.cursor()

    # query
    cursor.execute("SELECT * FROM budget")

    # get list of categories
    data = []
    for category, amount, amount_frequency, category_id in cursor:
        contents = {}
        contents["category"] = category
        contents["amount"] = amount
        contents["amount_frequency"] = amount_frequency
        contents["category_id"] = category_id
        data.append(contents)

    # close
    db_conn.close()

    # send data
    return jsonify(data)
