# -*- coding: utf-8 -*-
import time
from sys import argv
from graphs import GraphGenerator
from twitter import Twitter
import config

if __name__ == '__main__':
    time1 = time.time()
    twitter = Twitter(argv[1], argv[2])
    twitter._login()
    super_dict = {}
    user = ''
    following = twitter.get_following(user)
    followers = twitter.get_followers(user)
    super_dict[user] = {}
    super_dict[user]['following'] = following
    super_dict[user]['followers'] = followers
    user2 = ''
    following2 = twitter.get_following(user2)
    followers2 = twitter.get_followers(user2)
    super_dict[user2] = {}
    super_dict[user2]['following'] = following2
    super_dict[user2]['followers'] = followers2
    unique = following | followers | followers2 | following2
    config.print_("Processing " + str(len(unique)) + " accounts.")
    current = 1
    for twitter_user in unique:
        config.print_("Account #" + str(current))
        current += 1
        if twitter_user != user and twitter_user != user2:
            super_dict[twitter_user] = {}
            super_dict[twitter_user]['following'] = twitter.get_following(
                twitter_user, 50)
            super_dict[twitter_user]['followers'] = twitter.get_followers(
                twitter_user, 50)
    
    twitter._sign_out()
    g = GraphGenerator()
    for twitter_user in super_dict.keys():
        g.generate_follows_graph(twitter_user,
                                 super_dict[twitter_user]['following'],
                                 super_dict[twitter_user]['followers'])
    #g.generate_follows_intersect_graph(g.username, g.following, g.followers)
    #g.generate_follows_intersect_graph(user2, following2, followers2)
    time2 = time.time()
    config.print_(" Twinosy took : " + str(time2 - time1) + " seconds")
    g.paint()
    
