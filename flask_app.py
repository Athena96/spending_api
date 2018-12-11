from flask import Flask, jsonify
import sqlite3
from db_comms import DBCommms

# declare our Flask app
app = Flask(__name__)

# setup DB
DATABASE = '/home/inherentVice/spending_log.db'
db_comm = DBCommms(DATABASE)

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
    print((purchase_id))
    result = db_comm.delete_purchase(purchase_id)
    return result


@app.route('/<string:month>/<string:year>', methods=['GET'])
def get_spending_report(month, year):
    print("get_spending_report")
    print(get_spending_report)
    result = db_comm.get_spending_report(month, year)
    return result


@app.route('/budget', methods=['GET'])
def get_budget():
    print("get_budget()")
    result = db_comm.get_budget()
    return result

