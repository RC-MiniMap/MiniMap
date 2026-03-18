import json
import os

NODES_FILE = "data/nodes.json"
EDGES_FILE = "data/edges.json"


# JSON helpers

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


# Add Node

def add_node():
    print("\n--- Add New Node ---")

    node_id = input("Enter Node ID (e.g., room_101): ").strip()
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

    nodes = load_json(NODES_FILE)
    nodes.append(node)
    save_json(NODES_FILE, nodes)

    print(f"Node '{node_id}' added successfully.\n")


# Add Edge

def add_edge():
    print("\n--- Add New Edge ---")

    source = input("Enter Start Node ID: ").strip()
    target = input("Enter End Node ID: ").strip()
    edge_type = input("Enter Edge Type (hallway, stairs, elevator): ").strip()
    instruction = input("Enter Instruction (optional): ").strip()

    edge = {
        "source": source,
        "target": target,
        "type": edge_type,
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