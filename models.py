from datetime import datetime
from enum import Enum
from datetime import timedelta
from utilities import string_to_date

class RecurrenceType(Enum):
    INCOME = 1
    EXPENSE = 2

class BalanceRow:

    def __init__(self, balance_date, balance, income, expense, income_desc, expenses_desc):
        self.balance_date = balance_date
        self.balance = balance
        self.income = income
        self.expense = expense
        self.income_desc = income_desc
        self.expenses_desc = expenses_desc

class Category:

    def __init__(self, name, is_income):
        self.name = name
        self.is_income = is_income

    def __eq__(self, other):
        if isinstance(other, Category):
            return other.name == self.name and other.is_income == self.is_income
        else:
            return NotImplemented

class Transaction:

    def __init__(self, title, amount, category, date, description=None, credit_card=None, transaction_id=None):
        # this constructor should really just be assignments... this conversion should happen in another file.
        self.title = title
        self.amount = float(amount)

        categories = []
        first = True
        for c in category.split(","):
            if first:
                first = False
                categories.append(Category(name=c, is_income=True if self.amount > 0 else False))
            else:
                categories.append(Category(name=c, is_income=False))
        self.category = categories
        self.date = date
        self.description = description
        self.credit_card = credit_card
        self.transaction_id = transaction_id

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
        return contents

    def get_categories(self,):
        return list([c.name for c in self.category])

class Recurrence:

    def __init__(self, category, amount, amount_frequency, start_date, end_date, description=None, recurrence_id=None, type=None, repeat_start_date=None, days_till_repeat=None):
        self.type = RecurrenceType.EXPENSE if type is None else type
        self.amount = float(amount)
        self.category = Category(name=category, is_income=True if self.type == RecurrenceType.INCOME else False)
        self.amount_frequency = amount_frequency
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.recurrence_id = recurrence_id

        self.repeat_start_date = repeat_start_date
        self.days_till_repeat = days_till_repeat

        # start's on DATE, then repeats every x days (could be 14days, every other week) every 30 days 1x a month


    def to_dict(self):
        contents = {}
        contents["category"] = self.category.name
        contents["amount"] = self.amount
        contents["amount_frequency"] = self.amount_frequency
        contents["start_date"] = self.start_date
        contents["end_date"] = self.end_date
        contents["description"] = self.description
        contents["type"] = self.type
        contents["repeat_start_date"] = self.repeat_start_date
        contents["days_till_repeat"] = self.days_till_repeat
        contents["recurrence_id"] = self.recurrence_id
        return contents

    def generate_txn_days_in_range(self, clac_start_date, calc_end_date):
        txn_days = []
        txn_day = self.repeat_start_date

        while txn_day <= calc_end_date:
            if txn_day >= clac_start_date and txn_day <= calc_end_date:
                txn_days.append(txn_day)
            txn_day = txn_day + timedelta(days=self.days_till_repeat)

        return txn_days

class Period(Recurrence):

    def __init__(self, category, amount, start_date, end_date, description=None, recurrence_id=None, type=None, repeat_start_date=None, days_till_repeat=None):
        Recurrence.__init__(self, category, amount, "period", start_date, end_date, description=description, recurrence_id=recurrence_id, type=type)

    def get_date_month_year(self, is_start_date):
        if is_start_date:
            return "{}-{}-{}_{}:{}:{}".format(self.start_date[0:4], self.start_date[5:7], self.start_date[8:10], self.start_date[11:13], self.start_date[14:16], self.start_date[17:19])
        else:
            return "{}-{}-{}_{}:{}:{}".format(self.end_date[0:4], self.end_date[5:7], self.end_date[8:10], self.end_date[11:13], self.end_date[14:16], self.end_date[17:19])

class RecurrencePageInfo:

    def __init__(self, recurrence, spent_so_far_month, spent_so_far_year, spent_so_far_period=None):
        self.recurrence = recurrence

        if type(recurrence) is Period:
            self.spent_so_far_period = spent_so_far_period
            self.percent_period = (spent_so_far_period / recurrence.amount)
            self.remaining_period = "{}".format(round((recurrence.amount - spent_so_far_period), 2))
        else:
            self.percent_month = (spent_so_far_month / (recurrence.amount if recurrence.amount_frequency == "month" else (recurrence.amount / 12.0)))
            self.percent_year = (spent_so_far_year / (recurrence.amount if recurrence.amount_frequency == "year" else (recurrence.amount * 12.0)))
            if recurrence.amount_frequency == "month":
                self.remaining_month = "{}".format(round((recurrence.amount - spent_so_far_month), 2))

            self.remaining_year = "{}".format(round(((recurrence.amount if recurrence.amount_frequency == "year" else (recurrence.amount * 12.0)) - spent_so_far_year), 2))

        self.spent_so_far_month = "{}".format(round(spent_so_far_month, 2))
        self.spent_so_far_year = "{}".format(round(spent_so_far_year, 2))
