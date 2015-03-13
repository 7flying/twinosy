# -*- coding: utf-8 -*-
from os.path import isfile
import sqlite3 as lite
import config

class DBManager(object):
    """Class to handle the db."""
    conn = None
    
    def create_db(self, name):
        """Creates the db."""
        self.name = name
        if not isfile(self.name):
            self.connect()
            cursor = DBManager.conn.cursor()
            cursor.execute(
            """CREATE TABLE User (
               id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
               account TEXT NOT NULL UNIQUE);""")
            )
            cursor.execute(
            """CREATE TABLE Following (
               user INTEGER NOT NULL REFERENCES User (id) ON DELETE CASCADE,
               follows INTEGER NOT NULL REFERENCES User (id) ON DELETE CASCADE);
            """)
            cursor.execute(
            """CREATE TABLE Followers (
               user INTEGER NOT NULL REFERENCES User (id) ON DELETE CASCADE,
               follower INTEGER NOT NULL REFERENCES User (id) ON DELETE CASCADE);
            """)
            DBManager.conn.commit()
            self.disconnect()
            config.print_("Database created.")
        else:
            config.print_("The database is already created.")

    def connect(self):
		if DBManager.conn == None:
			try:
				DBManager.conn = lite.connect(self.name)
			except lite.Error, e:
				print "Exception %s" % e.args[0]

	def disconnect(self):
		if DBManager.conn:
			DBManager.conn.close()
			DBManager.conn = None

    def insert_user(self, account):
        cursor = DBManager.conn.cursor()
        cursor.execute("INSERT INTO User (account) VALUES (?);", (account,))

    
