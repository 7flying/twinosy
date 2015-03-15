import time
import re
from os import listdir
from random import randint
import networkx as nx
import matplotlib.pyplot as plt
from graph_tool.all import *
from manager import DBManager

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
    #plt.show()
    #plt.savefig("test2.png")
   

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
    manager.create_db('test.sqlite')
    manager.connect()
    files = listdir('files')
    print "%d files found" % len(files)
    matcher_followers = re.compile("^.+_followers\.txt$")
    matcher_following = re.compile("^.+_following\.txt$")
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
                manager.insert_followers(f[0:f.rfind('_')], users)
            else:
                print "ERRRRRRRROR with", f
                
    manager.disconnect()


if __name__ == '__main__':
    #test1()
    test2()
    #test3()
    #test4()
    #test5()
