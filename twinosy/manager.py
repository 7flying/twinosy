# -*- coding: utf-8 -*-
from os.path import isfile
from os import listdir
import re
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
        """Inserts a user."""
        cursor = DBManager.conn.cursor()
        cursor.execute("INSERT INTO User (account) VALUES (?);", (account,))
        DBManager.conn.commit()
        config.print_("User: " + account + " added")

    def _get_user_id(self, account):
        """Returns the user id from an account name."""
        cursor = DBManager.conn.cursor()
        cursor.execute("SELECT id FROM User WHERE account = ?;", (account,))
        result = cursor.fetchone()
        return result[0] if result != None and len(result) > 0 else None

    def is_account_created(self, account):
        """Checks whether an account is created."""
        return True if self._get_user_id(account) != None else False

    def has_follower(self, user, other):
        """Checks whether user has other as a follower."""
        user_id = self._get_user_id(user)
        other_id = self._get_user_id(other)
        if user_id != None and other_id != None:
            cursor  = DBManager.conn.cursor()
            cursor.execute("SELECT * FROM Followers" + 
                           " WHERE user = ? AND  follower = ?;", (user_id, other_id))
            result = cursor.fetchone()
            return True if result != None else False
        else:
            return False

    def is_following(self, user, other):
        """Checks whether user is following other."""
        user_id = self._get_user_id(user)
        other_id = self._get_user_id(other)
        if user_id != None and other_id != None:
            cursor  = DBManager.conn.cursor()
            cursor.execute("SELECT * FROM Following" + 
                           " WHERE user = ? AND  following = ?;",
                           (user_id, other_id))
            result = cursor.fetchone()
            return True if result != None else False
        else:
            return False

    def insert_followers(self, user, followers):
        """Inserts followers to a user."""
        if self.is_account_created(user):
            user_id = self._get_user_id(user)
            cursor = DBManager.conn.cursor()
            for foll in followers:
                if not self.is_account_created(foll):
                    self.insert_user(foll)
                if not self.has_follower(user, foll):
                    foll_id = self._get_user_id(foll)
                    cursor.execute("INSERT INTO Followers (user, follower)" +
                                   " VALUES (?, ?);", (user_id, foll_id))
                    DBManager.conn.commit()
                    config.print_("Added follower: " + foll + " to: " + user)

    def insert_following(self, user, following):
        """Inserts the accounts a user is following to."""
        if self.is_account_created(user):
            user_id = self._get_user_id(user)
            cursor = DBManager.conn.cursor()
            for foll in following:
                if not self.is_account_created(foll):
                    self.insert_user(foll)
                if not self.is_following(user, foll):
                    foll_id = self.get_user_id(foll)
                    cursor.execute("INSERT INTO Following (user, following)" +
                                   " VALUES (?, ?);", (user_id, foll_id))
                    DBManager.conn.commit()
                    config.print_("Added following: " + foll + " to: " + user)

def get_users(filename):
    f = open(filename, 'r')
    contents = [x for x in (f.read()).split(',') if len(x) > 0]
    f.close()
    return contents


if __name__ == '__main__':
    manager = DBManager()
    manager.create_db('test.sqlite')
    manager.connect()
    files = listdir('files')
    print "%d files found" % len(files)
    matcher_followers = re.compile("^.+_followers\.txt$")
    matcher_following = re.compile("^.+_following\.txt$")
    for f in files:
        if matcher_followers.match(f):
           users = get_users('files/' + f)
           if not manager.is_account_created(f[0:f.rfind('_')]):
               manager.insert_user(f[0:f.rfind('_')])
           manager.insert_followers(f[0:f.rfind('_')], users)
        else:
            if matcher_following.match(f):
                users = get_users('files/' + f)
                if not manager.is_account_created(f[0:f.rfind('_')]):
                    manager.insert_user(f[0:f.rfind('_')])
                manager.insert_followers(f[0:f.rfind('_')], users)
            else:
                print "ERRRRRRRROR with", f

    manager.disconnect()

