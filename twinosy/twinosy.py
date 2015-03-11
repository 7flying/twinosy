# -*- coding: utf-8 -*-
from graphs import GraphGenerator
from twitter import Twitter

if __name__ == '__main__':
    twitter = Twitter('tebores_', 'teborestwitter23')
    twitter._login()
    following = twitter.get_following('Seven_Flying')
    followers = twitter.get_followers('Seven_Flying')
    twitter._sign_out()
    g = GraphGenerator('Seven_Flying', followers, following)
    g.generate_my_follows_graph()
    g.paint()
