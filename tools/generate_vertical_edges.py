"""
generate_vertical_edges.py — Auto-generate inter-floor edges for elevators and staircases.

Reads nodes.json to discover which floors each connector exists on, then writes
bidirectional edges into data/edges.json.

    Elevators (E1, E3): all floor-pair combinations (elevators skip floors)
    Stairs (stairs_main, S1, S2): adjacent floors only (1↔2, 2↔3, etc.)

Usage:
    python tools/generate_vertical_edges.py
"""

import itertools
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NODES_PATH = REPO_ROOT / "data" / "nodes.json"
EDGES_PATH = REPO_ROOT / "data" / "edges.json"

ELEVATORS = {"E1", "E3"}
STAIRS = {"stairs_main", "S1", "S2"}
CONNECTORS = ELEVATORS | STAIRS


def load_json(path):
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def discover_connectors(nodes):
    """
    Scan nodes for known connector suffixes and return a dict of:
        suffix -> {"type": "elevator"|"staircase", "floors": [...], "name": str}
    """
    found = {}
    for node in nodes:
        node_id = node["id"]
        parts = node_id.split("_", 2)  # e.g. ["NPB", "5", "E1"] or ["NPB", "4", "stairs_main"]
        if len(parts) < 3:
            continue
        suffix = parts[2]
        if suffix not in CONNECTORS:
            continue
        floor = node["floor"]
        if suffix not in found:
            found[suffix] = {
                "type": "elevator" if suffix in ELEVATORS else "staircase",
                "floors": [],
                "name": node["name"],
                "building": node.get("building", "NPB"),
            }
        found[suffix]["floors"].append(floor)
    for suffix in found:
        found[suffix]["floors"].sort()
    return found


def make_edge(source_id, target_id, weight, instruction):
    return {"source": source_id, "target": target_id, "weight": weight, "instruction": instruction}


def generate_edges(connectors):
    new_edges = []
    for suffix, info in connectors.items():
        floors = info["floors"]
        building = info["building"]
        node_type = info["type"]

        if node_type == "elevator":
            pairs = list(itertools.combinations(floors, 2))
        else:
            pairs = [
                (floor_a, floor_b)
                for floor_a, floor_b in zip(floors, floors[1:])
                if floor_b == floor_a + 1
            ]

        for floor_a, floor_b in pairs:
            id_a = f"{building}_{floor_a}_{suffix}"
            id_b = f"{building}_{floor_b}_{suffix}"
            weight = abs(floor_b - floor_a) * 20

            if node_type == "elevator":
                instr_a_to_b = f"Take elevator {suffix} to floor {floor_b}."
                instr_b_to_a = f"Take elevator {suffix} to floor {floor_a}."
            else:
                instr_a_to_b = f"Take the stairs to floor {floor_b}."
                instr_b_to_a = f"Take the stairs to floor {floor_a}."

            new_edges.append(make_edge(id_a, id_b, weight, instr_a_to_b))
            new_edges.append(make_edge(id_b, id_a, weight, instr_b_to_a))

    return new_edges


def main():
    nodes = load_json(NODES_PATH)
    edges = load_json(EDGES_PATH)

    connectors = discover_connectors(nodes)
    if not connectors:
        print("No connectors found in nodes.json. Nothing to do.")
        return

    print("Discovered connectors:")
    for suffix, info in connectors.items():
        print(f"  {suffix} ({info['type']}): floors {info['floors']}")

    existing_pairs = {(e["source"], e["target"]) for e in edges}
    candidate_edges = generate_edges(connectors)

    added = 0
    skipped = 0
    for edge in candidate_edges:
        pair = (edge["source"], edge["target"])
        if pair in existing_pairs:
            skipped += 1
            continue
        edges.append(edge)
        existing_pairs.add(pair)
        added += 1

    save_json(EDGES_PATH, edges)
    print(f"\nDone: {added} edge(s) added, {skipped} skipped.")
    print(f"edges.json now has {len(edges)} total edges.")


if __name__ == "__main__":
    main()
