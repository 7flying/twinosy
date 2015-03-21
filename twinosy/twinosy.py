# -*- coding: utf-8 -*-
import time
from sys import argv
from graphs import GraphGenerator
from twitter import Twitter
from manager import DBManager
import config


def banner():
    print """ _____        _                   
|_   _|      (_)                      
  | |_      ___ _ __   ___  ___ _   _ 
  | \ \ /\ / / | '_ \ / _ \/ __| | | |
  | |\ V  V /| | | | | (_) \__ \ |_| |
  \_/ \_/\_/ |_|_| |_|\___/|___/\__, |
                                 __/ |
     The nosy Twitter analyser  |___/\n"""

def usage():
    banner()

def backup(file_name, what):
    f = open(file_name, 'w')
    for w in what:
        f.write(str(w) + ",")
    f.close()
    config.print_(file_name + " stored")


def scrap(user_list, dbname, botname, botpass, arffname=None):
    mag = DBManager()
    mag.connect(dbname)
    twitter = Twitter(botname, botpass)
    twitter._login()
    f = None
    if arffname != None:
        f = open(arffname, 'w')
        header = """
        @relation t-users\n@attribute user string\n@attribute following numeric\n@attribute followers numeric
        @attribute favourites numeric\n@attribute official {yes,no}\n@attribute description string
        @attribute desc_lang string\n@attribute $class$ {person,organization}\n\n@data\n"""
        f.write(header)
    progress = 1
    common_len = len(user_list)
    for user in user_list:
        num_foll = twitter.get_num_followers(user)
        db_foll = len(set(mag.get_followers(user)))
        if db_foll < num_foll:
            new_foll = twitter.get_followers(user)
            if new_foll != None:
                mag.insert_followers(user, new_foll)
        num_ing = twitter.get_num_following(user)
        db_ing = len(set(mag.get_following(user)))
        if db_ing < num_ing:
            new_foll = None
            new_foll = twitter.get_following(user)
            if new_foll != None:
                mag.insert_following(user, new_foll)
        favs = twitter.get_favourite_count(user)
        official = twitter.is_official(user)
        mag.insert_is_official(user, official)
        bio = twitter.get_user_bio(user)
        if bio != None and len(bio) > 0:
            mag.insert_bio(user, bio)
        else:
            bio = ' '
        if f != None:
            bio = bio.replace("'", "\'")
            official_str = 'yes' if official else 'no'
            sec = (user, str(num_ing), str(num_foll), str(favs), official_str,
                   u"'"+ bio + u"'", "'lang',CLASS\n")
            res = u','.join(sec)
            f.write(res.encode('utf-8'))
         print "Progress: " + str(progress) + " of " + common_len
         progress += 1
       
    twitter._sign_out()
    if f != None:
        f.close()
    mag.disconnect()

if __name__ == '__main__':
    usage()
    # set getopt and stuff
    scrap(list(argv[5:]), argv[1], argv[2], argv[3], argv[4])
