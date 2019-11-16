from datetime import datetime

from models import Recurrence
from models import RecurrenceType
from models import Transaction


def string_to_date(date_string):
    year = int(date_string.split("_")[0][0:4])
    month = int(date_string.split("_")[0][5:7])
    day = int(date_string.split("_")[0][8:10])
    return datetime(year=year, month=month, day=day)


def is_valid_or_none(string):
    val = None
    if string is not None and string != "NULL" and string != "None" and string != "null" and string != "nil" and string != "":
        val = string
    return val


def SQL_NULL_or_valid(opt_str):
    val = "NULL"
    if is_valid_or_none(opt_str) is not None:
        val = opt_str
    return val

def outside_to_python_transaction(title, amount, category, date, description, var_txn_tracking, txn_type,
                                  transaction_id=None):
    # title

    # amount
    amount = float(amount)

    # category
    categories = []
    if (len(category.split('-')) > 1):
        for category in category.split('-'):
            categories.append(category)
    else:
        categories.append(category)

    # date
    # create datetime obj

    # description
    description = is_valid_or_none(description)

    # var_txn_tracking
    var_txn_tracking = is_valid_or_none(var_txn_tracking)

    # txn_type
    txn_type = RecurrenceType.INCOME if int(txn_type) == 1 else RecurrenceType.EXPENSE

    # transaction_id
    transaction_id = is_valid_or_none(transaction_id)

    return Transaction(title=title, amount=amount, category=categories, date=date, description=description,
                       var_txn_tracking=var_txn_tracking, txn_type=txn_type, transaction_id=transaction_id)


def python_to_outside_transaction(transaction):
    print("python_to_outside_transaction()")
    writable_transaction = {}
    writable_transaction["title"] = transaction.title
    writable_transaction["amount"] = transaction.amount
    writable_transaction["category"] = "-".join(transaction.category)
    writable_transaction["date"] = transaction.date
    writable_transaction["description"] = SQL_NULL_or_valid(transaction.description)
    writable_transaction["var_txn_tracking"] = SQL_NULL_or_valid(transaction.var_txn_tracking)
    writable_transaction["txn_type"] = 1 if transaction.txn_type == RecurrenceType.INCOME else 2
    writable_transaction["transaction_id"] = SQL_NULL_or_valid(transaction.transaction_id)
    return writable_transaction


def outside_to_python_recurrence(name, amount, description, rec_type, start_date, end_date, days_till_repeat,
                                 day_of_month, recurrence_id=None):
    print("outside_to_python_recurrence()")
    # name

    # amount
    amount = float(amount)

    # description
    description = is_valid_or_none(description)

    # type
    rec_type = RecurrenceType.INCOME if int(rec_type) == 1 else RecurrenceType.EXPENSE

    # start_date
    start_date = None if is_valid_or_none(start_date) is None else string_to_date(start_date)

    # end_date
    end_date = None if is_valid_or_none(end_date) is None else string_to_date(end_date)

    # days_till_repeat
    days_till_repeat = is_valid_or_none(days_till_repeat)

    # day_of_month
    day_of_month = is_valid_or_none(day_of_month)

    # recurrence_id
    recurrence_id = is_valid_or_none(recurrence_id)

    return Recurrence(name=name, amount=amount, description=description, rec_type=rec_type, start_date=start_date,
                      end_date=end_date, days_till_repeat=days_till_repeat, day_of_month=day_of_month,
                      recurrence_id=recurrence_id)


def python_to_outside_recurrence(recurrence):
    print("python_to_outside_recurrence()")
    writable_recurrence = {}
    writable_recurrence["name"] = recurrence.name
    writable_recurrence["amount"] = recurrence.amount
    writable_recurrence["description"] = SQL_NULL_or_valid(recurrence.description)
    writable_recurrence["rec_type"] = 1 if recurrence.rec_type == RecurrenceType.INCOME else 2
    writable_recurrence["start_date"] = SQL_NULL_or_valid(recurrence.start_date)
    writable_recurrence["end_date"] = SQL_NULL_or_valid(recurrence.end_date)
    writable_recurrence["days_till_repeat"] = SQL_NULL_or_valid(recurrence.days_till_repeat)
    writable_recurrence["day_of_month"] = SQL_NULL_or_valid(recurrence.day_of_month)
    writable_recurrence["recurrence_id"] = SQL_NULL_or_valid(recurrence.recurrence_id)
    return writable_recurrence
