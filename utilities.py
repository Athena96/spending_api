from datetime import datetime

def string_to_date(date_string):
    year = int(date_string.split("_")[0][0:4])
    month = int(date_string.split("_")[0][5:7])
    day = int(date_string.split("_")[0][8:10])
    return datetime(year=year, month=month, day=day)
