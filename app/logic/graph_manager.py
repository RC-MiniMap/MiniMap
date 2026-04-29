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
        raise RuntimeError(
            f"Failed to load nodes data from {nodes_path}: {exc}"
        ) from exc
    try:
        with edges_path.open("r", encoding="utf-8") as f:
            edges_data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Failed to load edges data from {edges_path}: {exc}"
        ) from exc

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
        G.add_edge(edge["source"], edge["target"], **edge)
    return G


# should be used when graph is updated, to reload the graph with new data
def reload_graph():
    global G
    G = build_graph()


def shortest_route(graph, start, end):
    try:
        return nx.shortest_path(graph, source=start, target=end, weight="weight")
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
        {"id": n["id"], "name": n["name"]} for n in nodes_data if n["type"] == "room"
    ]
    return entrances, classrooms


# ---------------------------------------------------------------------------
# Dynamic turn-by-turn direction helpers
# ---------------------------------------------------------------------------


def compute_turn(prev_id, curr_id, next_id, G):
    """
    Compare the incoming edge (prev -> curr) with the outgoing edge
    (curr -> next) using a 2D cross product to determine turn direction.

    Coordinate system: math coords (positive Y = up, negative Y = down).
      cross > 0  ->  left turn   (counter-clockwise)
      cross < 0  ->  right turn  (clockwise)
      cross == 0 ->  straight

    For diagonal edges, each vector is projected onto its dominant axis
    (|dX| vs |dY|) before the comparison so that near-axis-aligned
    segments classify cleanly.
    """
    prev_coords = G.nodes[prev_id]["coords"]
    curr_coords = G.nodes[curr_id]["coords"]
    next_coords = G.nodes[next_id]["coords"]

    # Incoming edge vector (prev -> curr)
    dx_in = curr_coords[0] - prev_coords[0]
    dy_in = curr_coords[1] - prev_coords[1]

    # Outgoing edge vector (curr -> next)
    dx_out = next_coords[0] - curr_coords[0]
    dy_out = next_coords[1] - curr_coords[1]

    # Project each vector onto its dominant axis (handles diagonals)
    if abs(dx_in) >= abs(dy_in):
        dy_in = 0
    else:
        dx_in = 0

    if abs(dx_out) >= abs(dy_out):
        dy_out = 0
    else:
        dx_out = 0

    # 2D cross product
    cross = dx_in * dy_out - dy_in * dx_out

    if cross == 0:
        return "straight"
    elif cross > 0:
        return "left"
    else:
        return "right"


def get_landmark_label(node_id, G):
    """
    Build a human-readable landmark label based on node type.

    room       -> "Room {name}"
    elevator   -> "Elevator {name}"
    staircase  -> "Staircase {name}"
    spine      -> "the hallway"
    waypoint   -> "the hallway intersection"
    """
    node = G.nodes[node_id]
    node_type = node.get("type", "")
    name = node.get("name", node_id)

    if node_type == "room":
        return f"Room {name}"
    elif node_type == "elevator":
        return f"Elevator {name}"
    elif node_type == "staircase":
        return f"Staircase {name}"
    elif "_spine_" in node_id or node_type == "spine":
        return "the hallway"
    elif node_type == "waypoint":
        return "the hallway intersection"
    else:
        return name


def format_instruction(turn, next_id, G, is_final=False):
    """
    Build a natural-language instruction using the correct preposition.

    Preposition rules (based on the *next* node the user will reach):
      room / elevator  +  turn   -> "Turn {dir} into {label}."
      waypoint         +  turn   -> "Turn {dir} at {label}."
      spine            +  turn   -> "Turn {dir} into {label}."
      any              +  straight + destination -> "Continue straight toward {label}."
      waypoint/spine   +  straight              -> "Continue straight past {label}."
      final destination                         -> "You have arrived at {label}."
    """
    label = get_landmark_label(next_id, G)

    if is_final:
        return f"You have arrived at {label}."

    node = G.nodes[next_id]
    node_type = node.get("type", "")
    is_spine = "_spine_" in next_id or node_type == "spine"
    is_waypoint = node_type == "waypoint"
    is_destination = node_type in ("room", "elevator", "staircase")

    if turn == "straight":
        if is_destination:
            return f"Continue straight toward {label}."
        else:
            return f"Continue straight past {label}."
    else:  # left or right
        if is_destination:
            return f"Turn {turn} into {label}."
        elif is_waypoint:
            return f"Turn {turn} at {label}."
        elif is_spine:
            return f"Turn {turn} into {label}."
        else:
            return f"Turn {turn} at {label}."


def filter_straights(path, directions, coordinates, turn_types, G):
    if not directions:
        return directions, coordinates

    filtered_dirs = []
    filtered_coords = [coordinates[0]]

    for i in range(len(directions)):
        if turn_types[i] == "straight":
            next_id = path[i + 1]
            node = G.nodes[next_id]
            is_spine = "_spine_" in next_id or node.get("type") == "spine"
            is_waypoint = node.get("type") == "waypoint"

            if is_spine or is_waypoint:
                # Only drop if the NEXT step is also straight (true redundancy)
                next_turn = turn_types[i + 1] if i + 1 < len(turn_types) else None
                if next_turn == "straight":
                    continue  # redundant — skip it

        filtered_dirs.append(directions[i])
        filtered_coords.append(coordinates[i + 1])

    dest_coord = coordinates[-1]
    if not filtered_coords or filtered_coords[-1] != dest_coord:
        filtered_coords.append(dest_coord)

    return filtered_dirs, filtered_coords

# ---------------------------------------------------------------------------
# Main direction builder
# ---------------------------------------------------------------------------


def get_directions(start, end):
    """Generate turn-by-turn directions and coordinates from start to end."""
    global G
    if G is None:
        reload_graph()

    path = shortest_route(G, start, end)
    if path is None:
        return f"No path found from {start} to {end}."

    directions = []
    coordinates = []
    turn_types = []  # parallel list used by filter_straights

    # Trivial case: already there
    if start == end:
        directions.append("You are already at your destination.")
        current_node = G.nodes[start]
        coordinates.append(
            {
                "x": current_node["coords"][0],
                "y": current_node["coords"][1],
                "floor": current_node["floor"],
            }
        )
        return {"directions": directions, "coordinates": coordinates}

    for i in range(len(path)):
        current_node_id = path[i]
        current_node = G.nodes[current_node_id]

        coordinates.append(
            {
                "x": current_node["coords"][0],
                "y": current_node["coords"][1],
                "floor": current_node["floor"],
            }
        )

        if i == len(path) - 1:
            break

        next_node_id = path[i + 1]
        next_node = G.nodes[next_node_id]

        # --- Floor change (keep existing logic) ---
        if current_node["floor"] != next_node["floor"]:
            if (
                current_node.get("type") == "staircase"
                or next_node.get("type") == "staircase"
            ):
                directions.append(
                    f"Take the stairs from floor {current_node['floor']} to floor {next_node['floor']}."
                )
            else:
                directions.append(
                    f"Move from floor {current_node['floor']} to floor {next_node['floor']}."
                )
            turn_types.append("floor_change")

        # --- First edge: no previous node, so no turn to compute ---
        elif i == 0:
            label = get_landmark_label(next_node_id, G)
            directions.append(f"Head toward {label}.")
            turn_types.append("start")

        # --- Normal edge: compute turn dynamically ---
        else:
            prev_node_id = path[i - 1]
            turn = compute_turn(prev_node_id, current_node_id, next_node_id, G)
            instruction = format_instruction(turn, next_node_id, G)
            directions.append(instruction)
            turn_types.append(turn)

    # Collapse redundant spine straights before returning
    directions, coordinates = filter_straights(
        path, directions, coordinates, turn_types, G
    )

    return {"directions": directions, "coordinates": coordinates}


# builds photo of the graph
def main():
    global G
    nodes_data, _ = read_json_files()
    G = build_graph()
    # print(f"Successfully built graph!")
    # print(f"Nodes: {G.number_of_nodes()}")
    # print(f"Edges: {G.number_of_edges()}")
    pos = {
        node["id"]: tuple(node["coords"])
        for node in nodes_data
        if node.get("coords") and node["coords"][0] is not None
    }
    positioned_nodes = list(pos.keys())
    G_subgraph = G.subgraph(positioned_nodes).copy()
    nx.draw(
        G_subgraph,
        pos,
        with_labels=True,
        node_color="skyblue",
        node_size=2000,
        edge_color="black",
        font_size=10,
        font_weight="bold",
        arrowsize=20,
    )
    # plt.show()
    plt.savefig("map_preview.png")
    print("Map saved as map_preview.png - check your file list!")
    # print(G.edges())

    # #calcs shortest path between room_101 and room_102
    # print(shortest_route('room_101', 'room_102'))
    print(get_directions("NPB_5_102", "NPB_5_E1"))


if __name__ == "__main__":
    main()
