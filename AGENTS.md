# AGENTS.md

## Commands

```bash
uv run run.py                        # Run the app
FLASK_DEBUG=1 uv run run.py          # Run with debug mode

uv run ruff check .                  # Lint
uv run ruff format .                 # Format

uv run tools/generate_vertical_edges.py  # Regenerate inter-floor edges (elevators + stairs)
uv run tools/csv_import.py           # Bulk-import nodes from tools/npb_rooms.csv
```

No test suite. `GET /api/test` provides a quick sanity check against live data.

## Docker

```bash
docker compose up              # Dev: Flask, port 5000, debug on
docker compose -f docker-compose.prod.yml up   # Prod: Gunicorn 4 workers, port 5000
```

Python 3.14 required (see `.python-version`). `uv.lock` is gitignored — run `uv sync` before building Docker.

## Architecture

Flask app factory: `run.py` → `create_app()` → single blueprint registered from `routes.py`.

**Directions data flow:** `POST /directions` → `routes.py` → `graph_manager.get_directions(start, end)` → NetworkX `shortest_path` on a `DiGraph` loaded from `data/nodes.json` + `data/edges.json` → returns `{directions, coordinates}` → rendered in `index.html`.

## Graph singleton gotcha

`graph_manager.py` holds a module-level `DiGraph G`. First call to `get_directions()` or `get_options()` triggers `reload_graph()`. **After mutating `data/*.json` at runtime, call `reload_graph()` explicitly** or restart the server.

## Data format

- Node IDs: `{BUILDING}_{FLOOR}_{SUFFIX}` — e.g. `NPB_5_102`, `NPB_4_E1`, `NPB_3_stairs_main`
- Node types: `room`, `staircase`, `elevator`, `waypoint`, `spine`
- Edges are **directional and paired** — each physical connection needs two edge objects with different `instruction` strings. Weight = distance in the same unit as node coordinates (feet in the current data).
- `get_options()`: entrances = `type in ("elevator", "staircase")`, destinations = `type == "room"`

## Standalone tools (not imported by the app)

| File | Purpose |
|---|---|
| `tools/coord_picker.html` | Browser tool — click floor plan images to get pixel coordinates |
| `tools/edge_picker.html` | Browser tool — visually draw edges between nodes |
| `tools/csv_import.py` | Bulk-import nodes from CSV |
| `tools/generate_vertical_edges.py` | Auto-generate bidirectional stair/elevator edges across floors |

Known connectors for `generate_vertical_edges.py`: elevators `E1`, `E3` (all floor combos); stairs `stairs_main`, `S1`, `S2` (adjacent floors only).
