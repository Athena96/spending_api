from datetime import datetime
from datetime import timedelta

from models import BalanceRow
from models import RecurrenceType
from utilities import is_valid_or_none


class TimelineGenerator:

    def __init__(self, months_to_generate, db_comm, initial_recurrences, starting_balance, green_range, yellow_range):
        days_in_month = 31
        n = datetime.now()
        self.timeline_start_date = datetime(n.year, n.month, n.day)
        self.days_to_genrate = (days_in_month * months_to_generate)
        self.duration = timedelta(days=self.days_to_genrate)
        self.timeline_end_date = self.timeline_start_date + self.duration
        self.starting_balance = starting_balance
        self.db_comms = db_comm
        self.initial_recurrences = initial_recurrences
        self.green = 0.0
        self.yellow = 0.0
        self.red = 0.0
        self.green_range = green_range
        self.yellow_range = yellow_range

    def get_recurrences_for_day(self, date, rec_type):
        todays_recurrences = []
        recurrences = list(
            filter(lambda x: is_valid_or_none(x.repeat_start_date) is not None, self.initial_recurrences))
        todays_uncat_recurr = []  # todo

        for recurrence in recurrences:
            if rec_type == recurrence.rec_type and date in recurrence.generate_recurrence_days_in_range(self.timeline_start_date,
                                                                                                        self.timeline_end_date):

                # if it's a variable recurrence, then we need to query to see how much i've spent in
                # those variable categories, then update the 'amount' field of the Recurrence
                if recurrence.days_till_repeat is None and recurrence.day_of_month is None:
                    variable_txns = self.db_comms.get_transactions_with_var_tag(recurrence)
                    recurrence.amount = sum([x.amount for x in variable_txns])

                todays_recurrences.append(recurrence)

        total_amnt = round(sum([x.amount for x in todays_recurrences]), 2)
        total_descriptions = ",\r\n".join([x.description for x in todays_recurrences])
        return (total_amnt, total_descriptions)

    def generate_table(self):
        rows = []
        previous_bal = self.starting_balance
        greens = 0
        yellows = 0
        reds = 0

        for date in ([self.timeline_start_date + timedelta(days=x) for x in range(self.days_to_genrate)]):

            (incomes, income_desc) = self.get_recurrences_for_day(date, RecurrenceType.INCOME)
            (expenses, expenses_desc) = self.get_recurrences_for_day(date, RecurrenceType.EXPENSE)

            balance = round((previous_bal + incomes - expenses), 2)
            previous_bal = balance

            if balance >= self.green_range:
                bal_percent_color = "green"
                greens += 1
            elif balance < self.green_range and balance > self.yellow_range:
                bal_percent_color = "orange"
                yellows += 1
            else:
                bal_percent_color = "red"
                reds += 1

            rows.append(BalanceRow(balance_date=date, balance=balance, income=incomes, income_desc=income_desc,
                            expense=expenses, expenses_desc=expenses_desc, bal_percent_color=bal_percent_color))

        tot = greens + reds + yellows
        self.green = round(float(greens) / tot, 2)
        self.yellow = round(float(yellows) / tot, 2)
        self.red = round(float(reds) / tot, 2)
        return rows
