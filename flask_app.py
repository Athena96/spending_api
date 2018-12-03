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
    #rows = cursor.fetchall()
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


# Insert - POST
# @app.route('/<string:ticker>/<string:openPrice>/<string:closePrice>/<string:highPrice>/<string:lowPrice>/<string:volume>/<string:date>', methods=['POST'])
# def insertRecord(ticker, openPrice, closePrice, highPrice, lowPrice, volume, date):
#     # start transaction
#     #cursor.execute("START TRANSACTION;")
#
#     #savepointID = "insertSavepoint{0}".format(len(savepoints))
#     #savepoints.append( savepointID )
#
#     #cursor.execute("SAVEPOINT {0}".format(savepointID))
#
#     # alter table
#     # query the DB
#     cursor.execute("INSERT INTO StockData (ticker, openPrice, closePrice, highPrice, lowPrice, volume, date) VALUES ('{0}', {1}, {2},{3},{4},{5}, DATE '{6}');".format(ticker, openPrice, closePrice, highPrice, lowPrice, volume, date))
#
#     # mariadb_connection.commit()
#
#     iPhoneToken = 'eed50d343790b15fb440554457873a8730420c47abd789f07aa75003508039cf'
#
#     token_hex = '6523c10eee317c4cd614156972904a5467e0c47708551e4c8b78e7bd7a6e2507'
#
#     tokens = [iPhoneToken, token_hex]
#
#     alertString = "New price for {0}! ${1}".format(ticker, closePrice)
#
#     payload = ""
#     # payload = Payload(alert=alertString, sound="default", badge=1)
#     topic = 'com.new.CS411Project'
#     # client = APNsClient('apns-dev-cert.pem', use_sandbox=True, use_alternative_port=False)
#
#
#     #client.send_notification(token_hex, payload, topic)
#
#
#     return jsonify({'result': 'inserted'})

# Delete - DELETE
# @app.route('/<string:ticker>/<string:date>', methods=['DELETE'])
# def deleteRecord(ticker, date):
#     '''
#     A function that handles our DELETE API Endpoint.
#     More specificaly, the function is used to delete a tuple in our database.
#
#     - Parameters:
#     - cid: the cid for the tuple to be deleted
#
#     return: status msg
#     '''
#     print("deleteRecord()")
#
#     # query the DB
#     cursor.execute("DELETE FROM StockData WHERE ticker = '{0}' AND date = DATE '{1}';".format(ticker, date))
#
#     # mariadb_connection.commit()
#
#     return jsonify({'result': 'deleted'})

