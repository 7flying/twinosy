# -*- coding: utf-8 -*-
import time
from graphs import GraphGenerator
from twitter import Twitter
import config

if __name__ == '__main__':
    time1 = time.time()
    twitter = Twitter('', '')
    twitter._login()
    user = 'Seven_Flying'
    following = twitter.get_following(user)
    followers = twitter.get_followers(user)
    twitter._sign_out()
    #g = GraphGenerator(user, followers, following)
    #g.generate_my_follows_graph()
    #g.generate_follows_intersect_graph(g.username, g.following, g.followers)
    time2 = time.time()
    config.print_(" Twinosy took : " + str(time2 - time1) + " seconds")
    #g.paint()
    
