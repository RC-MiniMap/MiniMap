# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
uv run run.py

# Run with debug mode
FLASK_DEBUG=1 uv run run.py

# Lint
uv run ruff check .
uv run ruff format .

# Add nodes/edges via CLI
uv run app/logic/data_entry.py

# Regenerate inter-floor edges (elevators + stairs)
uv run tools/generate_vertical_edges.py
```

No test suite exists yet. The `/api/test` route (`GET /api/test`) provides a quick sanity check against live data.

## Architecture

Flask app factory pattern. `run.py` → `create_app()` → single blueprint registered from `routes.py`.

**Data flow for a directions request:**
```
POST /directions (entrance, classroom form params)
  → routes.py calls get_directions(start, end)
  → graph_manager.py: lazy-init module-level DiGraph G from data/nodes.json + data/edges.json
  → nx.shortest_path(G, source, target, weight='weight')
  → returns {directions: [...], coordinates: [{x, y, floor}, ...]}
  → rendered back into index.html
```

**Graph is a module-level singleton** in `graph_manager.py`. First call to `get_directions()` or `get_options()` triggers `reload_graph()`. Call `reload_graph()` explicitly after mutating `data/*.json` at runtime.

## Data Format

Node ID convention: `{BUILDING}_{FLOOR}_{SUFFIX}` — e.g. `NPB_5_102`, `NPB_4_E1`, `NPB_3_stairs_main`.

Node types: `room`, `staircase`, `elevator`, `waypoint`, `spine`.

Edges are **directional and paired** — every physical connection requires two edge objects with different `instruction` strings (one per direction). Weight is pixel distance.

`get_options()` filters entrances as `type in ("elevator", "staircase")` and destinations as `type == "room"`.

## Tools (not part of the running app)

| File | Purpose |
|---|---|
| `tools/coord_picker.html` | Open in browser to click floor plan and get pixel coords |
| `tools/edge_picker.html` | Visual tool to draw edges between nodes |
| `tools/csv_import.py` | Bulk-import nodes from `tools/npb_rooms.csv` |
| `tools/generate_vertical_edges.py` | Auto-generate bidirectional stair/elevator edges across floors |
| `app/logic/data_entry.py` | CLI for manually adding individual nodes and edges |

Known connectors for `generate_vertical_edges.py`: elevators `E1`, `E3` (all floor combinations); stairs `stairs_main`, `S1`, `S2` (adjacent floors only).
