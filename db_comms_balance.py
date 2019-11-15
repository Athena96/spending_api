from flask import jsonify

from db_comms import DBComms


class DBCommsBalance(DBComms):

    def __init__(self, database_path):
        DBComms.__init__(self, database_path)

    def set_starting_balance(self, starting_bal):
        print("     " + self.__class__.__name__)
        print("     " + "set_starting_bal({})".format(starting_bal))
        (self.db_conn, self.cursor) = self.get_instance()

        starting_bal = float(starting_bal)
        cmd = """UPDATE balance SET starting_bal = {} WHERE balance.starting_bal_id = 1""".format(starting_bal)
        self.cursor.execute(cmd)
        self.db_conn.commit()
        self.db_conn.close()
        print(cmd)

        return jsonify({'result': 'successfully updated starting_bal!'})

    def get_starting_balance(self):
        print("     " + self.__class__.__name__)
        print("     " + "get_starting_bal()")
        (self.db_conn, self.cursor) = self.get_instance()

        cmd = """select * from balance;"""

        self.cursor.execute(cmd)
        print(cmd)

        return self.extract_balance(self.cursor)

    def extract_balance(self, cursor):
        print("     " + self.__class__.__name__)
        print("     " + "extract_balance()")
        data = []
        for starting_bal_id, starting_bal in cursor:
            data.append(float(starting_bal))
            break

        return data[0]
