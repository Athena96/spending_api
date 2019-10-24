from datetime import datetime
from datetime import timedelta
from models import BalanceRow
from random import random

class TimelineGenerator:

    def __init__(self, months_to_generate):
        days_in_month = 30
        self.start_date = datetime.now()
        self.days_to_genrate = (days_in_month * months_to_generate)
        self.duration = timedelta(days=self.days_to_genrate)
        self.end_date = self.start_date + self.duration
        self.starting_balance = 2400.0

    def get_income_for_day(self, date):
        return (random()*1000, "ok")

    def get_expenses_for_day(self, date):
        return (random()*1000, "no")

    def generate_table(self):
        rows = []
        previous_bal = None
        for date in ([self.start_date + timedelta(days=x) for x in range(self.days_to_genrate)]):
            curr_date = date
            (income, income_desc) = self.get_income_for_day(curr_date)
            (expenses, expenses_desc) = self.get_expenses_for_day(curr_date)
            balance = self.starting_balance if previous_bal is None else (previous_bal + income - expenses)
            previous_bal = balance
            rows.append(BalanceRow(date, balance, income, income_desc, expenses, expenses_desc))
        return rows