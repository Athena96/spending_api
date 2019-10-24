from datetime import datetime
from datetime import timedelta
from models import BalanceRow
from random import random
from db_comms import DBCommms
from models import RecurrenceType

class TimelineGenerator:

    def __init__(self, months_to_generate, db_comms):
        days_in_month = 30
        n = datetime.now()
        yr = n.year
        mo = n.month
        day = n.day
        self.start_date = datetime(yr,mo,day)
        self.days_to_genrate = (days_in_month * months_to_generate)
        self.duration = timedelta(days=self.days_to_genrate)
        self.end_date = self.start_date + self.duration

        self.starting_balance = 2400.0
        self.db_comms = db_comms

    def get_recurrence_for_day(self, date, recurrence_type):
        # todo

        # -- Model Edit

        # Recurrence, should take the place of Budget and include functionalify for Income...
            # since both will be exactly the same... just add TYPE property to say if Income or Budget.
        # --

        # get list of ALL recurring incomes
            # where and Income is:
            #   - amount
            #   - description
            #   - category
            #   - start_date
            #   - days_till_repeat
        # get any uncategorized incomes that happened today

        # todays_incomes = []
        # for i in [incomes + today_uncat_income]:
        #   if today in i.pay_days_list():
        #       todays_incomes.append(i)
        if recurrence_type is RecurrenceType.INCOME:
            return (random()*1000, "ok")

        todays_recurrences = []
        recurrences = self.db_comms.get_budgets(date)
        todays_uncat_recurr = [] # todo

        for recurrence in recurrences:
            print("##HERE", recurrence.description)
            print("self.start_date", self.start_date)
            print("self.end_date", self.end_date)
            print("self.start_date", type(self.start_date))
            print("self.end_date", type(self.end_date))
            print("#date", date)
            print("#date", type(date))

            if date in recurrence.generate_txn_days_in_range(self.start_date, self.end_date):
                todays_recurrences.append(recurrence)

        total_amnt = (-1.0 if recurrence_type is RecurrenceType.EXPENSE else 1.0) * sum([x.amount for x in todays_recurrences])
        total_descriptions = ",\n".join([x.description for x in todays_recurrences])
        return (total_amnt, total_descriptions)

        #return (random()*1000, "ok")


    def generate_table(self):
        rows = []
        previous_bal = None
        for date in ([self.start_date + timedelta(days=x) for x in range(self.days_to_genrate)]):
            curr_date = date
            print("curr_date",curr_date)
            print("curr_date",type(curr_date))

            (income, income_desc) = self.get_recurrence_for_day(curr_date, RecurrenceType.INCOME)
            (expenses, expenses_desc) = self.get_recurrence_for_day(curr_date, RecurrenceType.EXPENSE)
            balance = self.starting_balance if previous_bal is None else (previous_bal + income - expenses)
            previous_bal = balance
            rows.append(BalanceRow(date, balance, income, income_desc, expenses, expenses_desc))
        return rows