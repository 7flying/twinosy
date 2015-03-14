# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt

class GraphGenerator(object):
    """Generates graphs"""
    def __init__(self, username=None, followers=set(), following=set()):
        self.username = username
        self.followers = followers
        self.following = following
        self.graph = nx.DiGraph()

    def generate_my_follows_graph(self):
        """Generates a graph taking into account the followers and following."""
        self.generate_follows_graph(self.username, self.following, self.followers)

    def generate_follows_graph(self, username, following, followers):
        """Generates the following-followers graph."""
        self.generate_following_graph(username, following)
        self.generate_followers_graph(username, followers)

    def generate_following_graph(self, username, following):
        """Generates the graph from a user to its followings."""
        self.graph.add_node(username)
        for user in following:
            self.graph.add_node(user)
            self.graph.add_edge(username, user)
            
    def generate_followers_graph(self, username, followers):
        """Generates a graph from a user to its followers."""
        self.graph.add_node(username)
        for user in followers:
            self.graph.add_node(user)
            self.graph.add_edge(user, username)

    def generate_follows_intersect_graph(self, username, following, followers):
        """Generates the intersection graph of followers and following."""
        interset = following & followers
        self.graph.add_node(username)
        for user in interset:
            self.graph.add_node(user)
            self.graph.add_edge(user, username)
            self.graph.add_edge(username, user)

    def paint(self):
        """Draws the graph."""
        pos = nx.graphviz_layout(self.graph)
        nx.draw_networkx_nodes(self.graph,pos,node_size=300,node_color='#9933FF'
                               ,alpha=0.4)
        nx.draw_networkx_edges(self.graph,pos,edge_color='#3399FF',node_size=0,
                       width=1,alpha=0.4)
        nx.draw_networkx_labels(self.graph,pos,fontsize=14)
        plt.axis('off')
        plt.show()

    def save_dot(self, filename):
        """Saves the graph as a dot file."""
        nx.write_dot(self.graph, filename)

    def load_dot(self, filename):
        """Loads a graoh from a dor file."""
        self.graph = nx.read_dot(filename)
