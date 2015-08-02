# -*- coding: utf-8 -*-

import os

from domain import Database, User
from twitter import TwitterAPI, TwitterScraper
from out import to_table, p_info

class Core(object):

    def __init__(self, shell):
        self.shell = shell
        self.twiapi = TwitterAPI()
        self.commands = { 'help' : {'desc': 'Display this help',
                                    'fn': self.core_help},
                          'exit' : {'desc': 'Exit Twinosy',
                                    'fn': self.core_exit},
                          'clear' : {'desc': 'Clear the terminal screen',
                                     'fn': self.core_clear},
                          'inspect' : {'desc': '',
                                       'fn': self.core_inspect}
                          }

    def core_help(self, *args):
        """Displays help"""
        rows = []
        for key in self.commands.keys():
            rows.append([key, self.commands[key]['desc']])
        p_info('Commands:')
        print to_table(['Command', 'Description'], rows)

    def core_exit(self, *args):
        """Exits twinosy"""
        self.shell.on = False

    def core_clear(self,*args):
        """Clear the terminal screen."""
        os.system('clear')
    
    def core_inspect(self, *args):
        """Inspects the given account retrieving basic user info."""
        # TODO Check account existance
        header1 = ['Account', 'Bio']
        header2 = ['Account', '# Tweets', '# Favs', '# Followers',
                   '# Following', 'Verified?']
        result1 = []
        result2 = []
        for account in args:
            result1.append([account, self.twiapi.get_user_bio(account)])
            result2.append([account, self.twiapi.get_num_tweets(account),
                            self.twiapi.get_num_favs(account),
                            self.twiapi.get_num_followers(account),
                            self.twiapi.get_num_following(account),
                            self.twiapi.is_official(account)])
        p_info('Inspect results:')
        print to_table(header1, result1)
        print to_table(header2, result2)
