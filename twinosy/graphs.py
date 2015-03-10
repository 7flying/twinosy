# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt

class GraphGenerator(object):
    """Generates graphs"""
    def __init__(self, username, followers=[], following=[]):
        self.username = username
        self.followers = followers
        self.following = following
        self.graph = nx.DiGraph()

    def generate_follows(self):
        """Generates a graph taking into account the followers and following."""
        self.graph.add_node(self.username)
        for unique in set(self.followers + self.following):
            self.graph.add_node(unique)
        for user in self.followers:
            self.graph.add_node(user, self.username)
        for user in self.following:
            self.graph.add_node(self.username, user)

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
