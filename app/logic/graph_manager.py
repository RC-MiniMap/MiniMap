import json
import networkx as nx
import matplotlib.pyplot as plt

from pathlib import Path
# modular graph
G = None

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
#should be used when graph is updated, to reload the graph with new data
def reload_graph():
    global G
    G = build_graph()
    

def shortest_route(graph, start, end):
    try:
        return nx.shortest_path(graph, source=start, target=end, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def get_floor_bounds(building, floor):
    repo_root = Path(__file__).resolve().parents[2]
    floors_path = repo_root / "data" / "floors.json"
    try:
        with floors_path.open("r", encoding="utf-8") as f:
            floors_data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load floors data from {floors_path}: {exc}") from exc
    floor_str = str(floor)
    try:
        floor_info = floors_data[building][floor_str]
    except KeyError:
        raise RuntimeError(f"No floor data for {building} floor {floor_str}")
    return {"width": floor_info["width_feet"], "height": floor_info["height_feet"]}


def get_options():
    nodes_data, _ = read_json_files()
    entrances = [
        {"id": n["id"], "name": n["name"]}
        for n in nodes_data
        if n["type"] in ("elevator", "staircase")
    ]
    classrooms = [
        {"id": n["id"], "name": n["name"]}
        for n in nodes_data
        if n["type"] == "room"
    ]
    return entrances, classrooms


#method to get direction
def get_directions(start, end):
    
    global G
    if G is None:
        reload_graph()
    
    path = shortest_route(G, start, end)
    if path is None:
        return f"No path found from {start} to {end}."
    directions = []
    coordinates = []
    if start == end:
        directions.append("You are already at your destination.")
        current_node = G.nodes[start]
        coordinates.append({"x": current_node["coords"][0], "y": current_node["coords"][1], "floor": current_node["floor"]})
        return {"directions": directions, "coordinates": coordinates}
    for i in range(len(path)):
        current_node_id = path[i]
        current_node = G.nodes[current_node_id]

        coordinates.append({
            "x": current_node["coords"][0],
            "y": current_node["coords"][1],
            "floor": current_node["floor"]
        })

        if i == len(path)-1:
            break

        next_node_id = path[i+1]
        next_node = G.nodes[next_node_id]
        edge_data = G.get_edge_data(current_node_id, next_node_id)

        #Detects when route changes floors
        #Staircases are treated as nodes and act as a transition point between floors, so we can check if the next node is a staircase and if the floor changes

        if current_node["floor"] != next_node["floor"]:
            if current_node.get("type") == "staircase" or next_node.get("type") == "staircase":
                directions.append(f"Take the stairs from floor {current_node['floor']} to floor {next_node['floor']}.")
            else:
                directions.append(f"Move from floor {current_node['floor']} to floor {next_node['floor']}.")
        else:
            directions.append(edge_data["instruction"])

    return {
        "directions": directions,
        "coordinates": coordinates
    }
#builds photo of the graph
def main():
    global G
    nodes_data, _ = read_json_files()
    G = build_graph()
    # print(f"Successfully built graph!")
    # print(f"Nodes: {G.number_of_nodes()}")
    # print(f"Edges: {G.number_of_edges()}")
    pos = {node["id"]: tuple(node["coords"]) for node in nodes_data
           if node.get("coords") and node["coords"][0] is not None}
    positioned_nodes = list(pos.keys())
    G_subgraph = G.subgraph(positioned_nodes).copy()
    nx.draw(
        G_subgraph,
        pos,
        with_labels=True,
        node_color='skyblue',
        node_size=2000,
        edge_color='black',
        font_size=10,
        font_weight='bold',
        arrowsize=20
    )
    #plt.show()
    plt.savefig("map_preview.png")
    print("Map saved as map_preview.png - check your file list!")
    #print(G.edges())

    # #calcs shortest path between room_101 and room_102
    # print(shortest_route('room_101', 'room_102'))
    print(get_directions('NPB_5_102', 'NPB_5_E1'))

if __name__ == "__main__":
    main()