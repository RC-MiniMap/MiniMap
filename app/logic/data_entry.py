import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
NODES_FILE = DATA_DIR / "nodes.json"
EDGES_FILE = DATA_DIR / "edges.json"


# JSON helpers

def load_json(path):
    path = Path(path)
    if not path.exists():
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON file '{path}': {e}")
            raise


def save_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# Add Node

def add_node():
    print("\n--- Add New Node ---")

    node_id = input("Enter Node ID (e.g., room_101): ").strip()

    # Load existing nodes and enforce unique node IDs
    nodes = load_json(NODES_FILE)
    if any(node.get("id") == node_id for node in nodes):
        print(f"Error: A node with ID '{node_id}' already exists. Please choose a different ID.\n")
        return

    x = float(input("Enter X coordinate: ").strip())
    y = float(input("Enter Y coordinate: ").strip())
    label = input("Enter Label (e.g., Kitchen): ").strip()
    node_type = input("Enter Node Type (room, hallway, waypoint, etc.): ").strip()
    floor = int(input("Enter Floor Number: ").strip())

    node = {
        "id": node_id,
        "name": label,
        "type": node_type,
        "coords": [x, y],
        "floor": floor
    }

    nodes.append(node)
    save_json(NODES_FILE, nodes)

    print(f"Node '{node_id}' added successfully.\n")


# Add Edge

def add_edge():
    print("\n--- Add New Edge ---")

    source = input("Enter Start Node ID: ").strip()
    target = input("Enter End Node ID: ").strip()
    weight = float(input("Enter Edge Weight (numeric cost): ").strip())
    instruction = input("Enter Instruction (optional): ").strip()

    # Validate that source and target node IDs exist
    nodes = load_json(NODES_FILE)
    existing_ids = {node.get("id") for node in nodes}

    missing = [nid for nid in (source, target) if nid not in existing_ids]
    if missing:
        print(
            "Error: The following node ID(s) do not exist and cannot be used in an edge: "
            + ", ".join(missing)
            + "\n"
        )
        return

    edge = {
        "source": source,
        "target": target,
        "weight": weight,
        "instruction": instruction
    }

    edges = load_json(EDGES_FILE)
    edges.append(edge)
    save_json(EDGES_FILE, edges)

    print(f"Edge between '{source}' and '{target}' added successfully.\n")


# Main Menu Loop

def main():
    while True:
        print("Floorplan Data Input Tool")
        print("1. Add Node")
        print("2. Add Edge")
        print("3. Exit")

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            add_node()
        elif choice == "2":
            add_edge()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()