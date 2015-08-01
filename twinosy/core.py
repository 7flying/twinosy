# -*- coding: utf-8 -*-

from domain import Database, User
from twitter import TwitterAPI, TwitterScraper

class Core(object):

    def __init__(self, shell):
        self.shell = shell
        self.twiapi = TwitterAPI()
        self.commands = { 'help' : {'desc': '', 'fn': self.core_help},
                          'exit' : {'desc': '', 'fn': self.core_exit},
                          'inspect' : {'desc': '', 'fn': self.core_inspect}
                          }

    def core_help(self, *args):
        """Displays help"""
        # TODO
        pass

    def core_exit(self, *args):
        """Exits twinosy"""
        self.shell.on = False
    
    def core_inspect(self, *args):
        """Inspects the given account retrieving basic user info."""
        account = args[0]
        # TODO Check account existance
        result = { 'Account' : account,
                   'Bio' : self.twiapi.get_user_bio(account),
                   '# Tweets' : self.twiapi.get_num_tweets(account),
                   # The number of favs must be retrieved using the scraper
                   #'# Favs' : self.twiapi.get_num_favs(account),
                   '# Followers' : self.twiapi.get_num_followers(account),
                   '# Following' : self.twiapi.get_num_following(account),
                   'Verified?' : self.twiapi.is_official(account)
                   }
        print result
