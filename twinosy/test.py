import networkx as nx
import matplotlib.pyplot as plt

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
dir_graph.add_edge("user-2", "user")

pos = nx.graphviz_layout(dir_graph)
nx.draw_networkx_nodes(dir_graph,pos,node_size=300,node_color='#9933FF',alpha=0.4)
nx.draw_networkx_edges(dir_graph,pos,edge_color='#3399FF',node_size=0,
                       width=1,alpha=0.4)
nx.draw_networkx_labels(dir_graph,pos,fontsize=14)
plt.axis('off')
plt.show()
