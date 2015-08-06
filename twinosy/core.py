# -*- coding: utf-8 -*-

import os

from domain import Database
from twitter import TwitterAPI
from out import to_table, p_info, p_error

class Core(object):

    def __init__(self, shell, db_name='.twinosy.db'):
        self.shell = shell
        self.db = Database(db_name)
        self.twiapi = TwitterAPI()
        self.twiapi.load_cache(self.db.create_cache())
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
        self.db.save_cache(self.twiapi.cache)

    def core_clear(self,*args):
        """Clear the terminal screen."""
        os.system('clear')

    def core_inspect(self, *args):
        """Inspects the given account retrieving basic user info."""
        g_info = ['Account', 'Name', 'ID', 'Bio']
        usage = ['Account', '# Tweets', '# Favs', '# Followers', '# Following']
        position = ['Account', 'Location', 'Time zone']
        acc_status = ['Account', 'Verified?', 'Suspended?', 'Protected?']
        g_info_r, usage_r, position_r, acc_sta_r = ([] for i in range(4))
        for account in args:
            if self.twiapi.check_account_existance(account):
                g_info_r.append([account, self.twiapi.get_user_name(account),
                                 self.twiapi.get_user_id(account),
                                 self.twiapi.get_user_bio(account)])
                usage_r.append([account, self.twiapi.get_num_tweets(account),
                                self.twiapi.get_num_favs(account),
                                self.twiapi.get_num_followers(account),
                                self.twiapi.get_num_following(account)])
                position_r.append([account,
                                   self.twiapi.get_user_location(account),
                                   self.twiapi.get_user_timezone(account)])
                acc_sta_r.append([account, self.twiapi.is_official(account),
                                  self.twiapi.is_suspended(account),
                                  self.twiapi.is_protected(account)])
            else:
                p_error("'" + account + "' does not exist")
        p_info('Inspect results:')
        if len(g_info_r) > 0 and len(position_r) > 0 and len(usage_r) > 0 and \
          len(acc_sta_r) > 0:
            p_info('General info:', 2)
            print to_table(g_info, g_info_r)
            p_info('Position:', 2)
            print to_table(position, position_r)
            p_info('Usage:', 2)
            print to_table(usage, usage_r)
            p_info('Account status:', 2)
            print to_table(acc_status, acc_sta_r)
        else:
            p_info('No results', 2)
