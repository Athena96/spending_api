from datetime import datetime

from models import Recurrence
from models import RecurrenceType
from models import Transaction


def get_day(balance_date):
    dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dt = "{}-{}-{}".format(balance_date.year, balance_date.month, balance_date.day)
    return "{} {}".format(dow[balance_date.weekday()], dt)

def get_date_page_links(type, db_comm_txn, ENVIRONMENT):
    print("Helper: root_page_helper({})".format(type))

    (min_year, month_year_list) = db_comm_txn.get_min_max_transaction_dates()
    final_year_links = []
    curr_year = min_year
    year_idx = 0
    year_first = True
    for (month, year) in month_year_list:
        if curr_year != year:
            curr_year = year
            year_idx += 1
            year_first = True

        month_str = "{:02d}".format(month)
        month_year_str = "{}-{}".format(month_str, year)
        link = "location.href='{}/site/{}/year:{}/month:{}'".format(ENVIRONMENT, type, year, month_str)

        if year_first:
            final_year_links.append((year, []))
            year_first = False

        final_year_links[year_idx][1].append((month_year_str, link))

    return ((obj[0], (sorted(obj[1], reverse=True))) for obj in sorted(final_year_links, reverse=True))

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

def outside_to_python_transaction(title, amount, category, date, description, payment_method, txn_type,
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

    # payment_method
    payment_method = is_valid_or_none(payment_method)

    # txn_type
    txn_type = RecurrenceType.INCOME if int(txn_type) == 1 else RecurrenceType.EXPENSE

    # transaction_id
    transaction_id = is_valid_or_none(transaction_id)

    return Transaction(title=title, amount=amount, category=categories, date=date, description=description,
                       payment_method=payment_method, txn_type=txn_type, transaction_id=transaction_id)


def python_to_outside_transaction(transaction):
    writable_transaction = {}
    writable_transaction["title"] = transaction.title
    writable_transaction["amount"] = transaction.amount
    writable_transaction["category"] = "-".join(transaction.category)
    writable_transaction["date"] = transaction.date
    writable_transaction["description"] = SQL_NULL_or_valid(transaction.description)
    writable_transaction["payment_method"] = SQL_NULL_or_valid(transaction.payment_method)
    writable_transaction["txn_type"] = 1 if transaction.txn_type == RecurrenceType.INCOME else 2
    writable_transaction["transaction_id"] = SQL_NULL_or_valid(transaction.transaction_id)
    return writable_transaction


def outside_to_python_recurrence(name, amount, description, rec_type, start_date, end_date, days_till_repeat,
                                 day_of_month, recurrence_id=None):
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
