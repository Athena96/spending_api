from datetime import datetime
from datetime import timedelta

from models import BalanceRow
from models import RecurrenceType

from utilities import get_day, outside_to_python_transaction

class TimelineGenerator:

    def __init__(self, months_to_generate, db_comm_txn, initial_recurrences, starting_balance, green_range,
                 yellow_range):
        days_in_month = 31
        n = datetime.now()
        self.timeline_start_date = datetime(n.year, n.month, n.day)
        self.days_to_genrate = (days_in_month * months_to_generate)
        self.duration = timedelta(days=self.days_to_genrate)
        self.timeline_end_date = self.timeline_start_date + self.duration
        self.starting_balance = starting_balance
        self.db_comm_txn = db_comm_txn
        self.initial_recurrences = initial_recurrences
        self.green = 0.0
        self.yellow = 0.0
        self.red = 0.0
        self.green_range = green_range
        self.yellow_range = yellow_range
        self.table = None

    def get_recurrences_for_day(self, date, rec_type):
        todays_recurrences = []

        for recurrence in self.initial_recurrences:
            if rec_type == recurrence.rec_type and date in recurrence.generate_recurrence_days_in_range(
                    self.timeline_start_date,
                    self.timeline_end_date):

                # if it's a variable recurrence, then we need to query to see how much i've spent in
                # those variable categories, then update the 'amount' field of the Recurrence
                if recurrence.days_till_repeat is None and recurrence.day_of_month is None and recurrence.amount == 0.0:
                    variable_txns = self.db_comm_txn.get_transactions_by_payment_method(recurrence.name)

                    recurrence.amount = sum([x.amount if x.txn_type is RecurrenceType.EXPENSE else (-1.0*x.amount) for x in variable_txns])

                todays_recurrences.append(recurrence)

        total_amnt = round(sum([x.amount for x in todays_recurrences]), 2)
        total_descriptions = ",\r\n".join([x.description for x in todays_recurrences])
        return (total_amnt, total_descriptions, todays_recurrences)


    def auto_add_todays_recurring_txns(self, recurrences, date):
        print("auto_add_todays_recurring_txns()")
        print("date: ", date)

        not_added_yet = True if len(self.db_comm_txn.get_auto_added_transaction_for_date(date)) == 0 else False

        if not_added_yet:
            for recurrence in recurrences:
                print("recurrence: ", recurrence.to_dict())
                transaction = outside_to_python_transaction(title="[AUTO_ADDED] {}".format(recurrence.description),
                                                            amount=recurrence.amount,
                                                            category=recurrence.name,
                                                            date=date,
                                                            description=recurrence.description,
                                                            payment_method="checking",
                                                            txn_type=recurrence.rec_type.value)
                self.db_comm_txn.add_transaction(transaction)


    def generate_table(self):

        if self.table is not None:
            print("balance_date", self.table[0].balance_date)
            print("type", type(self.table[0].balance_date))
            print("timeline_start_date", self.timeline_start_date)
            print("type", type(self.timeline_start_date))

            st_dt = self.table[0].balance_date.split(' ')[1].split('-')
            cached_date = datetime(year=int(st_dt[0]), month=int(st_dt[1]), day=int(st_dt[2]))
            today_date = self.timeline_start_date

            if cached_date == today_date:
                print("USING CACHE!")
                return self.table


        rows = []
        previous_bal = self.starting_balance
        greens = 0
        yellows = 0
        reds = 0

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
                greens += 1
            elif balance < self.green_range and balance > self.yellow_range:
                bal_percent_color = "orange"
                yellows += 1
            else:
                bal_percent_color = "red"
                reds += 1

            pretty_date = get_day(date)
            rows.append(BalanceRow(balance_date=pretty_date, balance=balance, income=incomes, income_desc=income_desc,
                                   expense=expenses, expenses_desc=expenses_desc, bal_percent_color=bal_percent_color))

        tot = greens + reds + yellows
        self.green = round(float(greens) / tot, 2)
        self.yellow = round(float(yellows) / tot, 2)
        self.red = round(float(reds) / tot, 2)
        self.table = rows
        return rows
