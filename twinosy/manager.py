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
               account TEXT NOT NULL UNIQUE,
               description TEXT,
               official INTEGER DEFAULT 0 CHECK(official=0 OR official=1));""")
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

    def connect(self,name=None):
        if name != None:
            self.name = name
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
        cursor.execute("INSERT INTO User (account) VALUES (?) ;", (account,))
        DBManager.conn.commit()
        config.print_("User: " + account + " added")

    def insert_bio(self, user, description):
        """Inserts a bio to the user."""
        if  description != None and len(description) > 0:
            cursor = DBManager.conn.cursor()
            user_id = self._get_user_id(user)
            if user_id != None:
                cursor.execute("UPDATE User SET description=? WHERE id =?;",
                               (description, user_id))
                DBManager.conn.commit()
                config.print_("Bio of " + user + " added")

    def insert_is_official(self, user, is_official):
        """Sets whether the user account is official or not, requires bool."""
        user_id = self._get_user_id(user)
        if user_id != None and type(is_official) == bool:
            cursor = DBManager.conn.cursor()
            cursor.execute("UPDATE User SET official=? WHERE id=?;",
                           (1 if is_official else 0, user_id))
            DBManager.conn.commit()
            config.print_("Added official=" + str(is_official) + " to " + user)

    def _get_user_account(self, user_id):
        """Given a user's id retrieves the account name."""
        cursor = DBManager.conn.cursor()
        cursor.execute("SELECT account FROM User WHERE id = ?;", (user_id,))
        result = cursor.fetchone()
        return result[0] if result != None and len(result) > 0 else None

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
                           " WHERE user = ? AND follows = ?;",
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
                    #config.print_("Added follower: " + foll + " to: " + user)

    def insert_following(self, user, following):
        """Inserts the accounts a user is following to."""
        if self.is_account_created(user):
            user_id = self._get_user_id(user)
            cursor = DBManager.conn.cursor()
            for foll in following:
                if not self.is_account_created(foll):
                    self.insert_user(foll)
                if not self.is_following(user, foll):
                    foll_id = self._get_user_id(foll)
                    cursor.execute("INSERT INTO Following (user, follows)" +
                                   " VALUES (?, ?);", (user_id, foll_id))
                    DBManager.conn.commit()
                    #config.print_("Added following: " + foll + " to: " + user)

    def get_users(self):
        """Retrieves all the users from the db."""
        cursor = DBManager.conn.execute("SELECT id, account FROM User;")
        ret = cursor.fetchall()
        cursor.close()
        return ret

    def get_followers(self, user):
        """Retrieves all the followers from a user."""
        follower_ids = self._get_followers_ids(user)
        if follower_ids != None:
            ret = [self._get_user_account(x[0])
                   for x in follower_ids if len(x) == 1]
            return ret
        else:
            return set()
            
    def _get_followers_ids(self, user):
        """Retrieves the follower ids from a user."""
        user_id = self._get_user_id(user)
        if user_id != None:
            cursor = DBManager.conn.execute("SELECT follower FROM Followers" +
                                            " WHERE user = ?;", (user_id,))
            ret = cursor.fetchall()
            cursor.close()
            return ret
        else:
            return None
    
    def get_following(self, user):
        """Retrieves all the following from a user."""
        following_ids = self._get_following_ids(user)
        if following_ids != None:
            ret = [self._get_user_account(x[0])
                   for x in following_ids if len(x) == 1]
            return ret
        else:
            return set()

    def _get_following_ids(self, user):
        """Retrieves the following ids from a user."""
        user_id = self._get_user_id(user)
        if user_id != None:
            cursor = DBManager.conn.execute("SELECT follows FROM Following" +
                                             " WHERE user = ?;", (user_id,))
            ret = cursor.fetchall()
            cursor.close()
            return ret
        else:
            return None

    def get_user_bio(self, user):
        """Retrieves the bio of a user."""
        user_id = self._get_user_id(user)
        ret = None
        if user_id != None:
            cursor = DBManager.conn.execute("SELECT description FROM User"
                                            + " WHERE id = ?;", (user_id,))
            ret = cursor.fetchone()
            cursor.close()
        return ret

    def is_official(self, user):
        """Checks whether the user account is official or not."""
        user_id = self._get_user_id(user)
        if user_id != None:
            cursor = DBManager.conn.execute("SELECT official FROM User"
                                            + " WHERE id = ?;", (user_id,))
            ret = cursor.fetchone()
            cursor.close()
            return ret == 1
        else:
            return None
