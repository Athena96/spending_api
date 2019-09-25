from datetime import datetime

def string_to_date(date_string):
    year = int(date_string.split("_")[0][0:4])
    month = int(date_string.split("_")[0][5:7])
    day = int(date_string.split("_")[0][8:10])
    return datetime(year=year, month=month, day=day)

def calculate_income_from(year_transactions, month):
    if month is None:
        return ("--", "--")
    year_income = round(sum([transaction.amount for transaction in year_transactions if transaction.category[0].is_income and int(transaction.date[5:7]) <= int(month)]), 2)
    month_income = round(sum([transaction.amount for transaction in year_transactions if (transaction.category[0].is_income and (transaction.date[5:7] == month))]), 2)
    return (year_income, month_income)