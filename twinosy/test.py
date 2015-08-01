# -*- coding: utf-8 -*-
import time
import re
import datetime
from os import listdir
from random import randint
from sys import argv
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from graph_tool.all import *
from twitter import Twitter
from graphs import GraphGenerator
from manager import DBManager

### Copy from twinosy.py ###
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

############################


def test1():
    graph = nx.Graph()

    graph.add_node("user")
    graph.add_node("user2")

    graph.add_edge("user", "user2")

    print "Number of nodes:", graph.number_of_nodes()
    print "Number of edges:", graph.number_of_edges()


    dir_graph = nx.DiGraph()
    dir_graph.add_node("user", account="@user")
    dir_graph.add_node("user-2", account="@user2")
    dir_graph.add_edge("user", "user-2")
    #dir(_graph.add_edge("user-2", "user")

    pos = nx.graphviz_layout(dir_graph)
    nx.draw_networkx_nodes(dir_graph,pos,node_size=300,node_color='#9933FF',alpha=0.4)
    nx.draw_networkx_edges(dir_graph,pos,edge_color='#3399FF',node_size=0,
                       width=1,alpha=0.4)
    nx.draw_networkx_labels(dir_graph,pos,fontsize=14)
    #nx.draw_graphviz(dir_graph)
    
    plt.axis('off')
    plt.show()

def test2():
    time_one = time.time()
    dir_graph = nx.DiGraph()
    total = 2000
    for i in range(total):
        account = "USER-" + str(i)
        dir_graph.add_node(str(i), account=account)
        if i != 0:
            if i == total - 1:
                dir_graph.add_edge(str(i), str(0))
            dir_graph.add_edge(str(i), str(i - 1))
            dir_graph.add_edge(str(i), str(randint(0, i)))
            
    time_two = time.time()
    print "Time took to add %d nodes & edges: %s" % (total, str((time_two - time_one)))
    pos = nx.graphviz_layout(dir_graph)
    nx.draw_networkx_nodes(dir_graph,pos,node_size=300,node_color='#9933FF',alpha=0.4)
    nx.draw_networkx_edges(dir_graph,pos,edge_color='#3399FF',node_size=0,
                       width=1,alpha=0.4)
    nx.draw_networkx_labels(dir_graph,pos,fontsize=14)
    plt.axis('off')
    time_three = time.time()
    print "Time took to paint the graph: %s" % (str(time_three - time_one))
    time_four = time.time()
    #nx.draw(dir_graph)
    nx.write_dot(dir_graph, "test2.dot") # then dot file.dot -T png > output.png
    print "Time took to generate dot file: %s" % (str(time_four - time_one))
    print "Total: %s" % (str(time_four - time_one))
    plt.show()
    plt.savefig(".png")
   

def test3():
    g = Graph()
    g.add_vertex(2) # Adds N vertices
    label = g.new_vertex_property("string")
    label[g.vertex(0)] = "some_0"
    label[g.vertex(1)] = "some_1" 
    g.add_edge(1, 0)
    graph_draw(g, vertex_text=label,output="test3.png")

def test4():
    g = Graph()
    g.add_vertex(2000) # Adds N vertices
    label = g.new_vertex_property("string")
    for i in range(2000):
        label[g.vertex(i)] = "USER" + str(i)
        if i != 0:
            g.add_edge(i, i-1)
    graph_draw(g, vertex_text=label, output_size=(2000,2000),output="test4.png")

def get_users(filename):
    f = open(filename, 'r')
    contents = [x for x in (f.read()).split(',') if len(x) > 0]
    f.close()
    return contents

def files_to_db():
    manager = DBManager()
    manager.create_db('twinosy-test.sqlite')
    manager.connect()
    files = listdir('files')
    print "%d files found" % len(files)
    matcher_followers = re.compile("^.+_followers\.txt$")
    matcher_following = re.compile("^.+_following\.txt$")
    time1 = time.time()
    pro = 1
    for f in files:
        if matcher_followers.match(f):
           users = get_users('files/' + f)
           if not manager.is_account_created(f[0:f.rfind('_')]):
               manager.insert_user(f[0:f.rfind('_')])
           manager.insert_followers(f[0:f.rfind('_')], users)
        else:
            if matcher_following.match(f):
                users = get_users('files/' + f)
                if not manager.is_account_created(f[0:f.rfind('_')]):
                    manager.insert_user(f[0:f.rfind('_')])
                manager.insert_following(f[0:f.rfind('_')], users)
            else:
                print "ERRRRRRRROR with", f
        print "Processed file %d out of %d!" % (pro, len(files))
        pro += 1
    manager.disconnect()
    time2 = time.time()
    print "DB created in " + str(time2 - time1)

def test5():
    twitter = Twitter(argv[1], argv[2])
    twitter._login()
    twitter._sign_out()

def test6():
    x = [1, 2, 4, 3]
    y = [1, 2, 3, 4]
    labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
              'Saturday', 'Sunday']
    #plt.plot(x, y, 'ro')
    plt.xticks(x, labels, rotation='vertical')
    plt.margins(0.2)
    plt.subplots_adjust(bottom=0.15)
    area = np.pi * 10 ** 2
    plt.scatter(x, y, s=area)
    plt.show()

def test7():
    twitter = Twitter(argv[1], argv[2])
    twitter._login()
    tweets_timedates = twitter.get_tweets_timedates_last('lifehacker', 200)
    day_plot_format = '%Y%m%d'
    time_plot_format = '%H.%M'
        
    counts = {}
    x = []
    y = []
    for tweet_time in tweets_timedates:
        d = datetime.datetime.strptime(tweet_time['timestamp'],
                                       '%I:%M %p - %d %b %Y')
                                    
        day = datetime.date.strftime(d, day_plot_format)
        time = datetime.date.strftime(d, time_plot_format)
        if day not in x:
            x.append(day)
        if time not in y:
            y.append(time)
        if day not in counts:
            counts[day] = {}
        if time not in counts[day]:
            counts[day][time] = 0
        counts[day][time] += 1
    twitter._sign_out()
    return counts

def test8(data):
    """
    data = {'20150212': {'2146': 1, '2156': 1},
            '20150309': {'2130': 1, '2236': 1},
            '20141206': {'0356': 1}, '20141030': {'1730': 1},
            '20141201': {'0049': 1, '2210': 1, '2334': 1, '0050': 1, '1819': 1,
                         '0045': 1},
            '20141202': {'0004': 1, '0006': 1, '0038': 1, '0107': 1, '1853': 1,
                         '0008': 1, '1922': 1, '1902': 1, '0051': 1},
            '20150121': {'2251': 1}, '20150114': {'1907': 1},
            '20150123': {'2240': 1}, '20141111': {'1004': 1, '1018': 1},
            '20150321': {'0009': 1}, '20150319': {'1243': 1},
            '20150323': {'1650': 1}, '20141120': {'0021': 1, '0018': 1},
            '20150306': {'2014': 1}, '20150317': {'1514': 1},
            '20150311': {'1932': 1, '2204': 1, '1640': 1},
            '20150312': {'0045': 1}, '20150128': {'2251': 1}}    
    """
    x = []
    y = []
    s = []
    for day in data.keys():
        for timestamp in data[day].keys():
            x.append(float(day))
            y.append(float(timestamp))
            s.append(np.pi * (data[day][timestamp] % 15) ** 2)
    plt.xticks([float(i) for i in sorted(data.keys())], sorted(data.keys()),
               rotation='vertical')
    print x
    print y
    plt.margins(0.2)
    plt.subplots_adjust(bottom=0.15)
    plt.scatter(x, y, s=s)
    plt.show()

def test9():
    """ Generate the network graph"""
    twitter = Twitter(argv[1], argv[2])
    twitter._login()
    followers = twitter.get_followers('', 300)
    following = twitter.get_following('', 300)
    twitter._sign_out()
    graph_gen = GraphGenerator('', followers=followers,
                               following=following)
    graph_gen.generate_follows_intersect_graph('', following,
                                                followers)
    graph_gen.save_dot('.dot')
    graph_gen.paint()

    
if __name__ == '__main__':
    #test1()
    #test2()
    #test3()
    #test4()
    #test6()
    #data = test7()
    #test8(data)
    #files_to_db()
    test9()
