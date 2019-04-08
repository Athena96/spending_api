class Transaction:

    def __init__(self, title, amount, category, date, note, transaction_id=None):
        self.title = title
        self.amount = amount
        self.category = category
        self.date = date
        if note == "--" or note == "NULL" or note == None or note == "":
            self.note = None
        else:
            self.note = note
        self.transaction_id = transaction_id

    def to_dict(self):
        contents = {}
        contents["transaction_id"] = self.transaction_id
        contents["title"] = self.title
        contents["amount"] = self.amount
        contents["category"] = self.category
        contents["date"] = self.date
        contents["note"] = self.note
        return contents


class Budget:

    def __init__(self, category, amount, amount_frequency, description=None, budget_id=None):
        self.category = category
        self.amount = amount
        self.amount_frequency = amount_frequency
        if description == "--" or description == "NULL" or description == None or description == "":
            self.description = None
        else:
            self.description = description
        self.budget_id = budget_id

    def get_startdate(self):
        if "special" in self.amount_frequency:
            parts = self.amount_frequency.split("_")
            startdate = parts[1]
            year = startdate[0:4]
            month = startdate[4:6]
            day = startdate[6:8]

            return (int(year), int(month), int(day))

    def get_duration(self):
        if "special" in self.amount_frequency:
            parts = self.amount_frequency.split("_")
            duration = parts[2]
            return int(duration)

    def to_dict(self):
        contents = {}
        contents["category"] = self.category
        contents["amount"] = self.amount
        contents["amount_frequency"] = self.amount_frequency
        contents["category_id"] = self.budget_id
        return contents

