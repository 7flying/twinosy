# -*- coding: utf-8 -*-

import os

from domain import Database, User
from twitter import TwitterAPI, TwitterScraper
from out import to_table, p_info

class Core(object):

    def __init__(self, shell):
        self.shell = shell
        self.twiapi = TwitterAPI()
        self.commands = {'help' : {'desc': 'Display this help',
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
        g_info = ['Account', 'Name', 'ID', 'Bio']
        usage = ['Account', '# Tweets', '# Favs', '# Followers', '# Following']
        position = ['Account', 'Location', 'Time zone']
        acc_status = ['Account', 'Verified?', 'Suspended?', 'Protected?']
        g_info_r, usage_r, position_r, acc_sta_r = ([] for i in range(4))
        for account in args:
            g_info_r.append([account, self.twiapi.get_user_name(account),
                             self.twiapi.get_user_id(account),
                             self.twiapi.get_user_bio(account)])
            usage_r.append([account, self.twiapi.get_num_tweets(account),
                            self.twiapi.get_num_favs(account),
                            self.twiapi.get_num_followers(account),
                            self.twiapi.get_num_following(account)])
            position_r.append([account, self.twiapi.get_user_location(account),
                               self.twiapi.get_user_timezone(account)])
            acc_sta_r.append([account, self.twiapi.is_official(account),
                              self.twiapi.is_suspended(account),
                              self.twiapi.is_protected(account)])
        p_info('Inspect results:')
        p_info('General info:', 2)
        print to_table(g_info, g_info_r)
        p_info('Position:', 2)
        print to_table(position, position_r)
        p_info('Usage:', 2)
        print to_table(usage, usage_r)
        p_info('Account status:', 2)
        print to_table(acc_status, acc_sta_r)
