from datetime import datetime

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

    def __init__(self, title, amount, category, date, description=None, transaction_id=None):
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
        self.transaction_id = transaction_id

    def to_dict(self):
        contents = {}
        contents["transaction_id"] = self.transaction_id
        contents["title"] = self.title
        contents["amount"] = self.amount
        contents["category"] = self.category.name
        contents["date"] = self.date
        contents["description"] = self.description
        return contents

    def get_categories(self,):
        return list([c.name for c in self.category])

class Budget:

    def __init__(self, category, amount, amount_frequency, start_date, end_date, description=None, budget_id=None):
        self.amount = float(amount)
        self.category = Category(name=category, is_income=True if self.amount > 0 else False)
        self.amount_frequency = amount_frequency
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.budget_id = budget_id

    def to_dict(self):
        contents = {}
        contents["category"] = self.category.name
        contents["amount"] = self.amount
        contents["amount_frequency"] = self.amount_frequency
        contents["start_date"] = self.start_date
        contents["end_date"] = self.end_date
        contents["description"] = self.description
        contents["budget_id"] = self.budget_id
        return contents

class Period(Budget):

    def __init__(self, category, amount, start_date, end_date, description=None, budget_id=None):
        Budget.__init__(self, category, amount, "period", start_date, end_date, description=description, budget_id=budget_id)

    def get_date_month_year(self, is_start_date):
        if is_start_date:
            return "{}-{}-{}_{}:{}:{}".format(self.start_date[0:4], self.start_date[5:7], self.start_date[8:10], self.start_date[11:13], self.start_date[14:16], self.start_date[17:19])
        else:
            return "{}-{}-{}_{}:{}:{}".format(self.end_date[0:4], self.end_date[5:7], self.end_date[8:10], self.end_date[11:13], self.end_date[14:16], self.end_date[17:19])

class BudgetPageInfo:

    def __init__(self, budget, spent_so_far_month, spent_so_far_year, spent_so_far_period=None):
        self.budget = budget
        num_rem_mo_in_yr = (12.0 - datetime.now().month)

        if type(budget) is Period:
            self.spent_so_far_period = spent_so_far_period
            self.percent_period = (spent_so_far_period / budget.amount)
            self.remaining_period = "{}".format(round((budget.amount - spent_so_far_period),2))
        else:
            self.percent_month = (spent_so_far_month / (budget.amount if budget.amount_frequency == "month" else (budget.amount / 12.0) ))
            self.percent_year = (spent_so_far_year / (budget.amount if budget.amount_frequency == "year" else (budget.amount * 12.0) ))

            if budget.amount_frequency == "month":
                self.remaining_month = "{}".format(round((budget.amount - spent_so_far_month),2))
                self.remaining_month_avg = "{}".format(round( (((budget.amount * 12.0) - spent_so_far_year) / num_rem_mo_in_yr) ,2))
            else:
                print("bud: ", budget.amount)
                print("spent_so_far_year: ", spent_so_far_year)
                self.remaining_month_avg = "{}".format(round( ((budget.amount - spent_so_far_year) / num_rem_mo_in_yr) ,2))

            self.remaining_year = "{}".format(round(((budget.amount if budget.amount_frequency == "year" else (budget.amount * 12.0)) - spent_so_far_year),2))

        self.spent_so_far_month = "{}".format(round(spent_so_far_month, 2))
        self.spent_so_far_year = "{}".format(round(spent_so_far_year, 2))
