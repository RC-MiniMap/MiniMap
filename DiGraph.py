import json
import networkx as nx
import matplotlib.pyplot as plt

from ShortestRoute import shortest_route

# read the JSON files
with open('data/nodes.json', 'r') as f:
    nodes_data = json.load(f)
with open('data/edges.json', 'r') as f:
    edges_data = json.load(f)

# create a directed graph
G = nx.DiGraph()
#method to add nodes
def add_nodes():
    for nodes in nodes_data:
        node_id = nodes["id"]
        G.add_node(node_id,**nodes)
#method to add edges
def add_edges():
    for edge in edges_data:
        G.add_edge(edge['source'], edge['target'], **edge)

#builds photo of the graph
add_nodes()
add_edges()
print(f"Successfully built graph!")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
pos = {node["id"]: tuple(node["coords"]) for node in nodes_data}
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='black', font_size=10, font_weight='bold', arrowsize=20)
#plt.show()
plt.savefig("map_preview.png")
print("Map saved as map_preview.png - check your file list!")
#print(G.edges())
#calcs shortest path between room_101 and room_102
print(shortest_route(G, 'room_101', 'room_102'))