from datetime import datetime
from enum import Enum
from datetime import timedelta
from utilities import get_variable_recurrence_transactions
from utilities import string_to_date

class RecurrenceType(Enum):
    INCOME = 1
    EXPENSE = 2

class BalanceRow:

    def __init__(self, balance_date, balance, income, expense, income_desc, expenses_desc, bal_percent=None):
        self.balance_date = balance_date
        self.balance = balance
        self.income = income
        self.expense = expense
        self.income_desc = income_desc
        self.expenses_desc = expenses_desc
        if balance >= 2374.75:
            self.bal_percent_color = "green"
        elif balance < 2374.75 and balance > 1187.375:
            self.bal_percent_color = "orange"
        else:
            self.bal_percent_color = "red"

class Transaction:

    def __init__(self, title, amount, category, date, description, var_txn_tracking, txn_type, transaction_id=None):
        self.title = title
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description
        self.var_txn_tracking = var_txn_tracking
        self.transaction_id = transaction_id
        self.txn_type = txn_type

    def get_transaction_day(self):
        dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        year = int(self.date.split("_")[0][0:4])
        month = int(self.date.split("_")[0][5:7])
        day = int(self.date.split("_")[0][8:10])
        date = datetime(year, month, day)
        return "{} {}".format(dow[date.weekday()], self.date[0:10])

    def get_transaction_day_date(self):
        year = int(self.date.split("_")[0][0:4])
        month = int(self.date.split("_")[0][5:7])
        day = int(self.date.split("_")[0][8:10])
        date = datetime(year, month, day)
        return date

    def to_dict(self):
        contents = {}
        contents["transaction_id"] = self.transaction_id
        contents["title"] = self.title
        contents["amount"] = self.amount
        contents["category"] = self.category[0].name
        contents["date"] = self.date
        contents["description"] = self.description
        contents["var_txn_tracking"] = self.var_txn_tracking
        contents["txn_type"] = self.txn_type
        return contents

    def get_categories(self,):
        return list([c.name for c in self.category])

class Recurrence:

    def __init__(self, name, amount, description, rec_type, start_date, end_date, days_till_repeat, day_of_month, recurrence_id=None):
        self.name = name
        self.amount = amount
        self.description = description
        self.rec_type = rec_type
        self.start_date = start_date
        self.end_date = end_date
        self.days_till_repeat = days_till_repeat
        self.day_of_month = day_of_month
        self.recurrence_id = recurrence_id

    def to_dict(self):
        contents = {}
        contents["name"] = self.name
        contents["amount"] = self.amount
        contents["description"] = self.description
        contents["rec_type"] = self.rec_type
        contents["start_date"] = self.start_date
        contents["end_date"] = self.end_date
        contents["days_till_repeat"] = self.days_till_repeat
        contents["day_of_month"] = self.day_of_month
        contents["recurrence_id"] = self.recurrence_id
        return contents

    def generate_txn_days_in_range(self, clac_start_date, calc_end_date):
        txn_day = self.repeat_start_date
        txn_days = [txn_day]

        e = string_to_date(self.end_date)
        if e < calc_end_date:
            calc_end_date = e

        while txn_day < calc_end_date and self.days_till_repeat != 0:
            if txn_day >= clac_start_date and txn_day <= calc_end_date:
                txn_days.append(txn_day)
            txn_day = txn_day + timedelta(days=self.days_till_repeat)

        return txn_days

class RecurrencePageInfo:

    def __init__(self, category, spent_so_far_month, spent_so_far_year):
        self.category = category
        self.spent_so_far_month = "{}".format(round(spent_so_far_month, 2))
        self.spent_so_far_year = "{}".format(round(spent_so_far_year, 2))