from datetime import datetime
from datetime import timedelta

from models import BalanceRow
from models import RecurrenceType
from models import TimelineStats
from utilities import get_day, convert_recurrance_to_transaction


class TimelineGenerator:

    def __init__(self, months_to_generate, db_comm_txn, initial_recurrences, green_range,
                 yellow_range):
        days_in_month = 31
        n = datetime.now()
        self.timeline_start_date = datetime(n.year, n.month, n.day)
        self.days_to_genrate = (days_in_month * months_to_generate)
        self.duration = timedelta(days=self.days_to_genrate)
        self.timeline_end_date = self.timeline_start_date + self.duration
        self.db_comm_txn = db_comm_txn
        self.initial_recurrences = initial_recurrences
        self.green_range = green_range
        self.yellow_range = yellow_range

    def get_recurrences_for_day(self, date, rec_type):
        todays_recurrences = []

        for recurrence in self.initial_recurrences:
            if rec_type == recurrence.rec_type and date in recurrence.generate_recurrence_days_in_range(
                    self.timeline_start_date,
                    self.timeline_end_date):

                # if it's a variable recurrence, then we need to query to see how much has been spent in
                # those variable categories, then update the 'amount' field of the Recurrence
                if recurrence.days_till_repeat is None and recurrence.day_of_month is None and recurrence.amount == 0.0:
                    variable_txns = self.db_comm_txn.get_transactions_by_payment_method(recurrence.name)

                    recurrence.amount = sum(
                        [x.amount if x.txn_type is RecurrenceType.EXPENSE else (-1.0 * x.amount) for x in
                         variable_txns])

                todays_recurrences.append(recurrence)

        total_amnt = round(sum([x.amount for x in todays_recurrences]), 2)
        total_descriptions = ",\r\n".join([x.description for x in todays_recurrences])
        return (total_amnt, total_descriptions, todays_recurrences)

    def auto_add_todays_recurring_txns(self, recurrences, date):
        not_added_yet = True if len(self.db_comm_txn.get_auto_added_transaction_for_date(date)) == 0 else False

        if not_added_yet:
            for recurrence in recurrences:
                transaction = convert_recurrance_to_transaction(recurrence, date)
                self.db_comm_txn.add_transaction(transaction)

    def generate_table(self, starting_balance):
        rows = []
        timeline_stats = TimelineStats()
        previous_bal = starting_balance

        today = True
        for date in ([self.timeline_start_date + timedelta(days=x) for x in range(self.days_to_genrate)]):
            (incomes, income_desc, income_recurrs) = self.get_recurrences_for_day(date, RecurrenceType.INCOME)
            (expenses, expenses_desc, expense_recurrs) = self.get_recurrences_for_day(date, RecurrenceType.EXPENSE)

            if today == True:
                self.auto_add_todays_recurring_txns(income_recurrs + expense_recurrs, date)
                today = False

            balance = round((previous_bal + incomes - expenses), 2)
            previous_bal = balance

            if balance >= self.green_range:
                bal_percent_color = "green"
                timeline_stats.green += 1
            elif balance < self.green_range and balance > self.yellow_range:
                bal_percent_color = "orange"
                timeline_stats.yellow += 1
            else:
                bal_percent_color = "red"
                timeline_stats.red += 1

            pretty_date = get_day(date)
            rows.append(BalanceRow(balance_date=pretty_date, balance=balance, income=incomes, income_desc=income_desc,
                                   income_recurrences=income_recurrs,
                                   expense_recurrences=expense_recurrs, expense=expenses, expenses_desc=expenses_desc,
                                   bal_percent_color=bal_percent_color))

        total = timeline_stats.green + timeline_stats.red + timeline_stats.yellow
        timeline_stats.green = round(float(timeline_stats.green) / total, 2)
        timeline_stats.yellow = round(float(timeline_stats.yellow) / total, 2)
        timeline_stats.red = round(float(timeline_stats.red) / total, 2)

        average_bal_num = round((sum([x.balance for x in rows]) / len(rows)), 2)
        timeline_stats.average_bal = "${}".format(average_bal_num)
        timeline_stats.average_bal_dff = "${}".format(round((average_bal_num - self.green_range), 2))

        return (rows, timeline_stats)
