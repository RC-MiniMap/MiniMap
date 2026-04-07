"""
csv_import.py — Bulk import rooms from CSV into data/nodes.json

Usage:
    python tools/csv_import.py [path/to/csv]

Defaults to tools/npb_rooms.csv if no path is given.

CSV format:
    id,name,building,floor,type
    NPB_1_101,1.101,NPB,1,room
    NPB_1_hallway_A,Hallway A,NPB,1,waypoint
"""

import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NODES_PATH = REPO_ROOT / "data" / "nodes.json"
DEFAULT_CSV = Path(__file__).resolve().parent / "npb_rooms.csv"


def load_nodes():
    if NODES_PATH.exists():
        with NODES_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_nodes(nodes):
    with NODES_PATH.open("w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2)


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV

    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    existing_nodes = load_nodes()
    existing_ids = {n["id"] for n in existing_nodes}

    added = 0
    skipped = 0
    new_nodes = list(existing_nodes)

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip comment rows or blank IDs
            node_id = row.get("id", "").strip()
            if not node_id or node_id.startswith("#"):
                continue

            if node_id in existing_ids:
                print(f"  SKIP (already exists): {node_id}")
                skipped += 1
                continue

            node = {
                "id": node_id,
                "name": row.get("name", node_id).strip(),
                "type": row.get("type", "room").strip(),
                "building": row.get("building", "").strip(),
                "coords": [0, 0],
                "floor": int(row.get("floor", 1)),
            }
            new_nodes.append(node)
            existing_ids.add(node_id)
            added += 1

    save_nodes(new_nodes)
    print(f"\nDone: {added} node(s) added, {skipped} skipped.")
    print(f"nodes.json now has {len(new_nodes)} total nodes.")


if __name__ == "__main__":
    main()
