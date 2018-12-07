from flask import Flask, jsonify
import sqlite3


class Purchase:

    def __init__(self, item, price, category, date, note=None):
        self.item = item
        self.price = price
        self.category = category
        self.date = date
        self.note = note


    # def add_purchase(self, purchase):
    #     self.cursor.execute(
    #         """INSERT INTO spending (item, price, category, date, note)
    #         VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(purchase.item,
    #         purchase.price, purchase.category, purchase.date, purchase.note))
    #     self.connection.commit()

# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'

@app.route('/<string:month>/<string:year>/<string:category>')
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



# Update - PUT
# @app.route('/<string:oldTicker>/<string:oldDate>/<string:ticker>/<string:openPrice>/<string:closePrice>/<string:highPrice>/<string:lowPrice>/<string:volume>/<string:date>', methods=['PUT'])
# def updateRecord(oldTicker, oldDate, ticker, openPrice, closePrice, highPrice, lowPrice, volume, date):
#     # query the DB
#     # SELECT ticker, openPrice, closePrice, highPrice, lowPrice, volume, CAST(date AS char)
#     cursor.execute("UPDATE StockData SET ticker = '{0}', openPrice = {1}, closePrice = {2}, highPrice = {3}, lowPrice = {4}, volume = {5}, date = DATE '{6}' WHERE ticker = '{7}' AND date = DATE '{8}';".format(ticker, openPrice, closePrice, highPrice, lowPrice, volume, date, oldTicker, oldDate))
#
#     # mariadb_connection.commit()
#
#     return jsonify({'result': 'updated'})
