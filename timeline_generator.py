from datetime import datetime
from datetime import timedelta
from models import BalanceRow
from random import random
from db_comms import DBCommms
from models import RecurrenceType
from utilities import get_variable_recurrence_transactions

class TimelineGenerator:

    def __init__(self, months_to_generate, db_comm):
        days_in_month = 30
        n = datetime.now()
        self.start_date = datetime(n.year,n.month,n.day)
        self.days_to_genrate = (days_in_month * months_to_generate)
        self.duration = timedelta(days=self.days_to_genrate)
        self.end_date = self.start_date + self.duration
        self.starting_balance = 2400.0
        self.db_comms = db_comm

    def get_recurrences_for_day(self, date, recurrence_type):

        todays_recurrences = []
        recurrences = self.db_comms.get_recurrences(date)
        todays_uncat_recurr = [] # todo

        for recurrence in recurrences:
            if recurrence_type == recurrence.type and date in recurrence.generate_txn_days_in_range(self.start_date, self.end_date):
                if recurrence.days_till_repeat == 0:
                    recurrence.amount = sum([x.amount for x in get_variable_recurrence_transactions(self.db_comms, recurrence)])

                todays_recurrences.append(recurrence)

        total_amnt = sum([x.amount for x in todays_recurrences])
        total_descriptions = ",\n".join([x.description for x in todays_recurrences])
        return (total_amnt, total_descriptions)

    def generate_table(self):
        rows = []
        previous_bal = None
        for date in ([self.start_date + timedelta(days=x) for x in range(self.days_to_genrate)]):
            (incomes, income_desc) = self.get_recurrences_for_day(date, RecurrenceType.INCOME)
            (expenses, expenses_desc) = self.get_recurrences_for_day(date, RecurrenceType.EXPENSE)
            balance = self.starting_balance if previous_bal is None else (previous_bal + incomes - expenses)
            previous_bal = balance
            rows.append(BalanceRow(date, balance, incomes, income_desc, expenses, expenses_desc))
        return rows