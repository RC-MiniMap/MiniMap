import json
from collections.abc import Mapping
from itertools import pairwise
from pathlib import Path
from typing import Any

import networkx as nx

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_graph: nx.DiGraph | None = None


def navigate(selection: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Build a complete template model for one navigation request."""
    try:
        nodes, edges, floors = _load_map_facts()
    except RuntimeError as exc:
        return _outcome(status="error", error=str(exc))

    outcome = _outcome(
        entrances=_options(nodes, {"elevator", "staircase"}),
        classrooms=_options(nodes, {"room"}),
    )
    if selection is None:
        return outcome

    start = selection.get("entrance")
    destination = selection.get("classroom")
    if not start or not destination:
        outcome.update(status="error", error="Missing entrance or classroom parameter")
        return outcome

    graph = _get_graph(nodes, edges)
    try:
        path = nx.shortest_path(
            graph, source=start, target=destination, weight="weight"
        )
    except nx.NetworkXNoPath, nx.NodeNotFound:
        outcome.update(
            status="error",
            error=(
                "No route could be found between the selected entrance and "
                "destination. Please check your selections and try again."
            ),
        )
        return outcome

    directions, coordinates = _describe_path(graph, path)
    traversed_floors = list(dict.fromkeys(point["floor"] for point in coordinates))
    outcome.update(
        status="success",
        directions=directions,
        traversed_floors=traversed_floors,
    )

    if not coordinates:
        outcome["map"] = {
            "status": "unavailable",
            "data": None,
            "message": "Map preview is unavailable for this route.",
        }
    elif len(traversed_floors) > 1:
        outcome["map"] = {
            "status": "unavailable",
            "data": None,
            "message": (
                "Map preview is unavailable for routes spanning multiple floors. "
                "Follow the directions panel for this route."
            ),
        }
    else:
        first_node = graph.nodes[path[0]]
        try:
            bounds = _floor_bounds(floors, first_node["building"], traversed_floors[0])
        except RuntimeError as exc:
            outcome.update(status="error", error=str(exc))
            return outcome
        outcome["map"] = {
            "status": "ready",
            "data": {"coordinates": coordinates, "bounds": bounds},
            "message": None,
        }

    return outcome


def _outcome(
    *,
    status: str = "idle",
    error: str | None = None,
    entrances: list[dict[str, str]] | None = None,
    classrooms: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "error": error,
        "directions": [],
        "traversed_floors": [],
        "map": {"status": "idle", "data": None, "message": None},
        "options": {
            "entrances": entrances or [],
            "classrooms": classrooms or [],
        },
    }


def _load_map_facts() -> tuple[list[dict], list[dict], dict]:
    return (
        _read_json("nodes.json", "nodes"),
        _read_json("edges.json", "edges"),
        _read_json("floors.json", "floors"),
    )


def _read_json(filename: str, label: str):
    """Read json data from given filename, return dict"""
    path = _DATA_DIR / filename
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Failed to load {label} data from {path}: {exc}") from exc


def _options(nodes: list[dict], node_types: set[str]) -> list[dict[str, str]]:
    """Given a dict of nodes and a set of node types, return a list of dicts filtered by the set of node types"""
    return [
        {"id": node["id"], "name": node["name"]}
        for node in nodes
        if node["type"] in node_types
    ]


def _get_graph(nodes: list[dict], edges: list[dict]) -> nx.DiGraph:
    """If nonexistent, DiGraph is built from nodes and edges"""
    global _graph
    if _graph is None:
        graph = nx.DiGraph()
        for node in nodes:
            graph.add_node(node["id"], **node)
        for edge in edges:
            graph.add_edge(edge["source"], edge["target"], **edge)
        _graph = graph
    return _graph


def _describe_path(
    graph: nx.DiGraph, path: list[str]
) -> tuple[list[str], list[dict[str, int | float]]]:
    coordinates = [_coordinate(graph.nodes[node_id]) for node_id in path]
    if len(path) == 1:
        return ["You are already at your destination."], coordinates

    directions = [
        _transition_instruction(
            graph.nodes[current_id],
            graph.nodes[next_id],
            graph.get_edge_data(current_id, next_id),
        )
        for current_id, next_id in pairwise(path)
    ]
    return directions, coordinates


def _coordinate(node: dict) -> dict[str, int | float]:
    """Given a node (dict) return a dict with 3 keys: x, y, and floor"""
    return {"x": node["coords"][0], "y": node["coords"][1], "floor": node["floor"]}


def _transition_instruction(current: dict, next_node: dict, edge: dict) -> str:
    if current["floor"] == next_node["floor"]:
        return edge["instruction"]
    if "staircase" in {current.get("type"), next_node.get("type")}:
        return (
            f"Take the stairs from floor {current['floor']} "
            f"to floor {next_node['floor']}."
        )
    if current.get("type") == next_node.get("type") == "elevator":
        return edge["instruction"]
    return f"Move from floor {current['floor']} to floor {next_node['floor']}."


def _floor_bounds(floors: dict, building: str, floor: int) -> dict[str, int | float]:
    """Given floors data dict, building str, and floor number, return floor bounds as a simple width and height dict"""
    floor_key = str(floor) # convert int representation of floor into a str
    try:
        floor_info = floors[building][floor_key] 
        # extract floor metadata from specific building and floor
    except KeyError as exc:
        # key not found, meaning either floor or building data isn't present
        raise RuntimeError(f"No floor data for {building} floor {floor_key}") from exc
    return {"width": floor_info["width_feet"], "height": floor_info["height_feet"]} # return floor bounds as simple width and height dict


