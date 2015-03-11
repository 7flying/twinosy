# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt

class GraphGenerator(object):
    """Generates graphs"""
    def __init__(self, username, followers=set(), following=set()):
        self.username = username
        self.followers = followers
        self.following = following
        self.graph = nx.DiGraph()

    def generate_follows_graph(self):
        """Generates a graph taking into account the followers and following."""
        self.graph.add_node(self.username)
        for unique in self.followers | self.following:
            self.graph.add_node(unique)
        for user in self.followers:
            self.graph.add_edge(user, self.username)
        for user in self.following:
            self.graph.add_edge(self.username, user)

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

if __name__ == '__main__':
    followers = set(['one', 'two', 'three', 'four'])
    following = set(['one', 'tree', 'five', 'nine', 'eleven'])
    graph = GraphGenerator('USER', followers, following)
    graph.generate_follows_graph()
    graph.paint()
