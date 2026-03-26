import json
import networkx as nx
import matplotlib.pyplot as plt

from pathlib import Path

# read the JSON files
def read_json_files():
    """
    Load nodes and edges JSON data using deterministic paths.
    The data directory is resolved relative to the repository root,
    assumed to be two levels above this file (app/logic/graph_manager.py).
    """
    # Resolve repo root as two levels up from this file: app/logic -> app -> repo root
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "data"
    nodes_path = data_dir / "nodes.json"
    edges_path = data_dir / "edges.json"
    try:
        with nodes_path.open("r", encoding="utf-8") as f:
            nodes_data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load nodes data from {nodes_path}: {exc}") from exc
    try:
        with edges_path.open("r", encoding="utf-8") as f:
            edges_data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load edges data from {edges_path}: {exc}") from exc
    
    return nodes_data, edges_data


def build_graph():
    nodes_data, edges_data = read_json_files()
    # create a directed graph
    G = nx.DiGraph()
    # method to add nodes and edges
    for node in nodes_data:
        node_id = node["id"]
        G.add_node(node_id, **node)
    for edge in edges_data:
        G.add_edge(edge['source'], edge['target'], **edge)
    return G


def shortest_route(graph, start, end):
    try:
        return nx.shortest_path(graph, source=start, target=end, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


#method to get direction
def get_directions(start, end):
    graph = build_graph()
    path = shortest_route(graph, start, end)
    if path is None:
        return "No path found"
    directions = []
    coordinates = []
    #grabs directions
    for i in range(len(path) - 1):
        edge_data = graph.get_edge_data(path[i], path[i + 1])
        directions.append(edge_data['instruction'])
        coordinates.append(graph.nodes[path[i]]['coords'])
    #if start and end are the same, add a message to directions
    if (start == end):
        directions.append("You are already at your destination.")
    return directions, coordinates

#builds photo of the graph
def main():
    nodes_data, _ = read_json_files()
    G = build_graph()
    # print(f"Successfully built graph!")
    # print(f"Nodes: {G.number_of_nodes()}")
    # print(f"Edges: {G.number_of_edges()}")
    pos = {node["id"]: tuple(node["coords"]) for node in nodes_data}
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='black', font_size=10, font_weight='bold', arrowsize=20)
    #plt.show()
    plt.savefig("map_preview.png")
    print("Map saved as map_preview.png - check your file list!")
    #print(G.edges())

    # #calcs shortest path between room_101 and room_102
    # print(shortest_route('room_101', 'room_102'))
    print(get_directions('room_102', 'room_101'))

if __name__ == "__main__":
    main()