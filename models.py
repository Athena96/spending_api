class Purchase:

    def __init__(self, item, price, category, date, note, purchase_id=None):
        self.item = item
        self.price = price
        self.category = category
        self.date = date
        self.note = note # set to None if not present
        self.purchase_id = purchase_id


class Budget:

    def __init__(self, category, amount, amount_frequency, budget_id=None):
        self.category = category
        self.amount = amount
        self.amount_frequency = amount_frequency
        self.budget_id = budget_id
