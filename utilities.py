from datetime import datetime

def string_to_date(date_string):
    year = int(date_string.split("_")[0][0:4])
    month = int(date_string.split("_")[0][5:7])
    day = int(date_string.split("_")[0][8:10])
    return datetime(year=year, month=month, day=day)

def is_valid_or_none(string):
    val = None
    if string is not None and string != "NULL" and string != "None" and string != "null" and string != "nil" and string != "":
        val = string
    return val