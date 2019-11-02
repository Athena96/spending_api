from datetime import datetime
from datetime import timedelta
from models import BalanceRow
from db_comms import DBCommms
from models import RecurrenceType
from utilities import get_variable_recurrence_transactions
from utilities import is_valid_or_none

class TimelineGenerator:

    def __init__(self, months_to_generate, db_comm, initial_recurrences=None, starting_balance=None):
        days_in_month = 31
        n = datetime.now()
        self.start_date = datetime(n.year,n.month,n.day)
        self.days_to_genrate = (days_in_month * months_to_generate)
        self.duration = timedelta(days=self.days_to_genrate)
        self.end_date = self.start_date + self.duration
        self.starting_balance = starting_balance
        self.db_comms = db_comm
        self.initial_recurrences = initial_recurrences
        self.green = 0.0
        self.yellow = 0.0
        self.red = 0.0

    def get_recurrences_for_day(self, date, recurrence_type):
        todays_recurrences = []
        recurrences = list(filter(lambda x: is_valid_or_none(x.repeat_start_date) is not None, self.initial_recurrences))
        todays_uncat_recurr = [] # todo

        for recurrence in recurrences:
            if recurrence_type == recurrence.type and date in recurrence.generate_txn_days_in_range(self.start_date, self.end_date):
                if recurrence.days_till_repeat == 0 and "variable" in recurrence.amount_frequency and recurrence.amount == 0.0:
                    var_txns = self.db_comms.get_cc_transactions_for_statement(recurrence)
                    recurrence.amount = sum([x.amount for x in var_txns])
                todays_recurrences.append(recurrence)

        total_amnt = round(sum([x.amount for x in todays_recurrences]),2)
        total_descriptions = ",\r\n".join([x.description for x in todays_recurrences])
        return (total_amnt, total_descriptions)

    def generate_table(self):
        rows = []
        previous_bal = self.starting_balance
        greens = 0
        yellows = 0
        reds = 0

        for date in ([self.start_date + timedelta(days=x) for x in range(self.days_to_genrate)]):
            (incomes, income_desc) = self.get_recurrences_for_day(date, RecurrenceType.INCOME)
            (expenses, expenses_desc) = self.get_recurrences_for_day(date, RecurrenceType.EXPENSE)
            balance = (previous_bal + incomes - expenses)
            balance = round(balance, 2)
            previous_bal = balance
            br = BalanceRow(balance_date=date, balance=balance, income=incomes, income_desc=income_desc, expense=expenses, expenses_desc=expenses_desc)
            rows.append(br)
            if br.bal_percent_color == "green":
                greens += 1
            elif br.bal_percent_color == "orange":
                yellows += 1
            else:
                reds += 1

        tot = greens + reds + yellows
        self.green = round(float(greens)/tot, 2)
        self.yellow = round(float(yellows)/tot, 2)
        self.red = round(float(reds)/tot, 2)
        return rows