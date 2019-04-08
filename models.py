
class Transaction:

    def __init__(self, title, amount, category, date, description=None, transaction_id=None):
        self.title = title
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description
        self.transaction_id = transaction_id

    def to_dict(self):
        contents = {}
        contents["transaction_id"] = self.transaction_id
        contents["title"] = self.title
        contents["amount"] = self.amount
        contents["category"] = self.category
        contents["date"] = self.date
        contents["description"] = self.description
        return contents

class Budget:

    def __init__(self, category, amount, amount_frequency, description=None, budget_id=None):
        self.category = category
        self.amount = amount
        self.amount_frequency = amount_frequency
        self.description = description
        self.budget_id = budget_id

    def to_dict(self):
        contents = {}
        contents["category"] = self.category
        contents["amount"] = self.amount
        contents["amount_frequency"] = self.amount_frequency
        contents["budget_id"] = self.budget_id
        return contents

class SpecialBudget(Budget):

    def __init__(self, category, amount, amount_frequency, description=None, budget_id=None):
        Budget.__init__(self, category, amount, amount_frequency, description=None, budget_id=None)

        parts = self.amount_frequency.split("_")
        startdate = parts[1]
        year = startdate[0:4]
        month = startdate[4:6]
        day = startdate[6:8]
        self.start_date = (int(year), int(month), int(day))

        parts = self.amount_frequency.split("_")
        self.duration = int(parts[2])


    # def __init__(self, category, amount, start_date, duration, description=None, budget_id=None):
    #     amount_frequency = "special_{}{}{}_{}".format(start_date[0], start_date[1], start_date[2], duration)
    #     Budget.__init__(self, category, amount, amount_frequency, description=None, budget_id=None)
    #     self.start_date = start_date
    #     self.duration = duration
