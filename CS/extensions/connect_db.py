import psycopg2
from os.path import dirname


# a class for a connection object
class DBConnection:

    # the constructor
    def __init__(self):
        # some arguments for psycopg2.connect()
        DBNAME = 'clash'
        USER = 'clashuser'
        HOST = '10.32.95.90'
        PASSWORD_FILE = '{}/../credentials/psql-pass.txt'.format(dirname(__file__))

        # try to open password file to connect to DB
        try:
            pgpass_file = open(PASSWORD_FILE)
        except OSError:
            print('ERROR: Cannot open credential file.')
            exit(1)

        # try to read in password
        passwd = pgpass_file.readline()
        if len(passwd) == 0:
            print('ERROR: Empty credential file.')
            exit(1)

        # try to create a DB connection
        try:
            self.con = psycopg2.connect(
                database=DBNAME,
                user=USER,
                host=HOST,
                password=passwd
            )
        except psycopg2.Error as e:
            print('ERROR: Cannot connect: {}.'.format(str(e).strip()))
            exit(1)

        self.con.set_session(autocommit=True)  # allow this for simplicity

    # returns the connection
    def get_con(self):
        return self.con
