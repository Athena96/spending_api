from flask import jsonify

from db_comms import DBComms
from utilities import outside_to_python_recurrence
from utilities import python_to_outside_recurrence


class DBCommsRecurrence(DBComms):

    def __init__(self, database_path):
        DBComms.__init__(self, database_path)

    def add_recurrence(self, recurrence):
        print("     " + self.__class__.__name__)
        print("     " + "add_recurrence({})", recurrence)
        (self.db_conn, self.cursor) = self.get_instance()

        writable_recurr = python_to_outside_recurrence(recurrence)
        cmd = """INSERT INTO recurrences (name, amount, description, rec_type, start_date, end_date, days_till_repeat, day_of_month) VALUES ('{}', {}, '{}', {}, '{}', '{}', {}, {})""".format(
            writable_recurr["name"], writable_recurr["amount"], writable_recurr["description"],
            writable_recurr["rec_type"],
            writable_recurr["start_date"],
            writable_recurr["end_date"], writable_recurr["days_till_repeat"], writable_recurr["day_of_month"])
        self.cursor.execute(cmd)
        self.db_conn.commit()
        self.db_conn.close()
        print(cmd)

        return jsonify({'result': 'successfully added recurrence category!'})

    def update_recurrence(self, recurrence):
        print("     " + self.__class__.__name__)
        print("     " + "update_recurrence({})", recurrence)
        (self.db_conn, self.cursor) = self.get_instance()

        recurrenceMP = python_to_outside_recurrence(recurrence)
        cmd = """UPDATE recurrences SET name = '{}', amount = {}, description = '{}', rec_type = {}, start_date = '{}', end_date = '{}', days_till_repeat = {}, day_of_month = {} WHERE recurrences.recurrence_id = {}""".format(
            recurrenceMP["name"], recurrenceMP["amount"], recurrenceMP["description"], recurrenceMP["rec_type"],
            recurrenceMP["start_date"],
            recurrenceMP["end_date"], recurrenceMP["days_till_repeat"], recurrenceMP["day_of_month"],
            recurrenceMP["recurrence_id"])
        self.cursor.execute(cmd)
        self.db_conn.commit()
        print(cmd)

        return jsonify({'result': 'successfully updated recurrence category!'})

    def delete_recurrence(self, recurrence_id):
        print("     " + self.__class__.__name__)
        print("     " + "delete_recurrence({})", recurrence_id)
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = "DELETE FROM recurrences WHERE recurrences.recurrence_id = {0};".format(int(recurrence_id))
        self.cursor.execute(cmd)
        self.db_conn.commit()
        print(cmd)

        return jsonify({'result': 'successfully deleted recurrence category!'})

    def get_recurrences(self, date=None):
        print("     " + self.__class__.__name__)
        print("     " + "get_recurrences({})".format(date))
        (self.db_conn, self.cursor) = self.get_instance()

        if date is None:
            cmd = """select * from recurrences;"""
        else:
            cmd = """select * from recurrences where recurrences.start_date <= '{0}-{1}-{2} {3}:{4}:{5}' and recurrences.end_date >= '{0}-{1}-{2} {3}:{4}:{5}' """.format(
                date.year,
                '{:02d}'.format(date.month),
                '{:02d}'.format(date.day),
                '{:02d}'.format(date.hour),
                '{:02d}'.format(date.minute),
                '{:02d}'.format(date.second))
        self.cursor.execute(cmd)
        print(cmd)

        return self.extract_recurrence(self.cursor)

    def get_recurrence(self, recurrence_id):
        print("     " + self.__class__.__name__)
        print("     " + "get_recurrence({})".format(recurrence_id))
        (self.db_conn, self.cursor) = self.get_instance()

        if recurrence_id is None:
            return None

        cmd = """select * from recurrences where recurrences.recurrence_id = {}""".format(recurrence_id)
        self.cursor.execute(cmd)
        print(cmd)

        result = self.extract_recurrence(self.cursor)
        return None if len(result) == 0 or len(result) > 1 else result[0]

    def extract_recurrence(self, cursor):
        print("     " + self.__class__.__name__)
        print("     " + "extract_recurrence()")
        data = []
        for recurrence_id, name, amount, description, rec_type, start_date, end_date, days_till_repeat, day_of_month in cursor:
            recurrence = outside_to_python_recurrence(name=name, amount=amount, description=description,
                                                      rec_type=rec_type,
                                                      start_date=start_date, end_date=end_date,
                                                      days_till_repeat=days_till_repeat, day_of_month=day_of_month,
                                                      recurrence_id=recurrence_id)
            data.append(recurrence)

        return data
