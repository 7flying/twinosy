# -*- coding: utf-8 -*-
import time
from sys import argv
from graphs import GraphGenerator
from twitter import Twitter
import config

def backup(file_name, what):
    f = open(file_name, 'w')
    for w in what:
        f.write(str(w) + ",")
    f.close()
    config.print_(file_name + " stored")

if __name__ == '__main__':
    time1 = time.time()
    twitter = Twitter(argv[1], argv[2])
    twitter._login()
    super_dict = {}
    user2 = ''
    following2 = twitter.get_following(user2)
    backup(user2 + '_following.txt', following2)
    followers2 = twitter.get_followers(user2)
    backup(user2 + '_followers.txt', followers2)
    super_dict[user2] = {}
    super_dict[user2]['following'] = following2
    super_dict[user2]['followers'] = followers2
    user = ''
    following = twitter.get_following(user)
    backup(user + '_following.txt',following)
    followers = twitter.get_followers(user)
    backup(user + '_followers.txt', followers)
    super_dict[user] = {}
    super_dict[user]['following'] = following
    super_dict[user]['followers'] = followers
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
            backup(twitter_user + '_following.txt',
                   super_dict[twitter_user]['following'])
            super_dict[twitter_user]['followers'] = twitter.get_followers(
                twitter_user, 50)
            backup(twitter_user + '_followers.txt',
                   super_dict[twitter_user]['followers'])
    
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
    
