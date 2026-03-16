import json
import networkx as nx
import matplotlib.pyplot as plt

# read the JSON files
with open('data/nodes.json', 'r') as f:
    nodes_data = json.load(f)
with open('data/edges.json', 'r') as f:
    edges_data = json.load(f)

# create a directed graph
G = nx.DiGraph()

for nodes in nodes_data:
    node_id = nodes["id"]
    G.add_node(node_id,**nodes)
for edge in edges_data:
    G.add_edge(edge['source'], edge['target'], **edge)

print(f"Successfully built graph!")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
nx.draw(G, with_labels=True, node_color='skyblue', node_size=2000, edge_color='black', font_size=10, font_weight='bold', arrowsize=20)
#plt.show()
plt.savefig("map_preview.png")
print("Map saved as map_preview.png - check your file list!")