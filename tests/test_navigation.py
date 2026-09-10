import json

import networkx as nx
import pytest

from app import logic
from app.logic import navigation


@pytest.fixture(autouse=True)
def reset_graph_cache():
    navigation._graph = None
    yield
    navigation._graph = None


def node(node_id, *, floor=1, node_type="waypoint", x=0, y=0, building="BLDG"):
    return {
        "id": node_id,
        "name": node_id,
        "type": node_type,
        "building": building,
        "coords": [x, y],
        "floor": floor,
    }


def facts(nodes, edges=(), floors=None):
    if floors is None:
        floors = {"BLDG": {"1": {"width_feet": 100, "height_feet": 80}}}
    return nodes, list(edges), floors


def select(start="start", destination="end"):
    return {"entrance": start, "classroom": destination}


def test_idle_outcome_contains_options(monkeypatch):
    nodes = [
        node("elevator", node_type="elevator"),
        node("stairs", node_type="staircase"),
        node("room", node_type="room"),
        node("hall"),
    ]
    monkeypatch.setattr(navigation, "_load_map_facts", lambda: facts(nodes))

    outcome = navigation.navigate()

    assert outcome["status"] == "idle"
    assert outcome["options"] == {
        "entrances": [
            {"id": "elevator", "name": "elevator"},
            {"id": "stairs", "name": "stairs"},
        ],
        "classrooms": [{"id": "room", "name": "room"}],
    }
    assert outcome["map"]["status"] == "idle"


@pytest.mark.parametrize(
    "selection",
    [
        {},
        {"entrance": "start"},
        {"classroom": "end"},
        {"entrance": "", "classroom": "end"},
    ],
)
def test_navigation_rejects_missing_selection(monkeypatch, selection):
    monkeypatch.setattr(navigation, "_load_map_facts", lambda: facts([]))

    outcome = navigation.navigate(selection)

    assert outcome["status"] == "error"
    assert outcome["error"] == "Missing entrance or classroom parameter"


def test_navigation_returns_one_map_ready_outcome_for_weighted_path(monkeypatch):
    nodes = [
        node("start", node_type="elevator", x=1, y=2, building="NPB"),
        node("direct", x=20),
        node("detour", x=3, y=4, building="NPB"),
        node("end", node_type="room", x=5, y=6, building="NPB"),
    ]
    edges = [
        {"source": "start", "target": "direct", "weight": 10, "instruction": "Direct."},
        {"source": "direct", "target": "end", "weight": 10, "instruction": "Finish."},
        {
            "source": "start",
            "target": "detour",
            "weight": 2,
            "instruction": "Walk ahead.",
        },
        {
            "source": "detour",
            "target": "end",
            "weight": 3,
            "instruction": "Turn right.",
        },
    ]
    floors = {"NPB": {"1": {"width_feet": 300, "height_feet": 60}}}
    monkeypatch.setattr(
        navigation, "_load_map_facts", lambda: facts(nodes, edges, floors)
    )

    outcome = navigation.navigate(select())

    assert outcome["status"] == "success"
    assert outcome["directions"] == ["Walk ahead.", "Turn right."]
    assert outcome["traversed_floors"] == [1]
    assert outcome["map"] == {
        "status": "ready",
        "data": {
            "coordinates": [
                {"x": 1, "y": 2, "floor": 1},
                {"x": 3, "y": 4, "floor": 1},
                {"x": 5, "y": 6, "floor": 1},
            ],
            "bounds": {"width": 300, "height": 60},
        },
        "message": None,
    }


def test_navigation_uses_node_building_instead_of_parsing_id(monkeypatch):
    nodes = [
        node("unstructured-start", building="NPB"),
        node("end", node_type="room", building="NPB"),
    ]
    edges = [
        {
            "source": "unstructured-start",
            "target": "end",
            "weight": 1,
            "instruction": "Arrive.",
        }
    ]
    floors = {"NPB": {"1": {"width_feet": 20, "height_feet": 10}}}
    monkeypatch.setattr(
        navigation, "_load_map_facts", lambda: facts(nodes, edges, floors)
    )

    outcome = navigation.navigate(select("unstructured-start"))

    assert outcome["map"]["data"]["bounds"] == {"width": 20, "height": 10}


def test_navigation_handles_same_start_and_destination(monkeypatch):
    nodes = [node("room", node_type="room", x=12, y=-3)]
    monkeypatch.setattr(navigation, "_load_map_facts", lambda: facts(nodes))

    outcome = navigation.navigate(select("room", "room"))

    assert outcome["directions"] == ["You are already at your destination."]
    assert outcome["map"]["data"]["coordinates"] == [{"x": 12, "y": -3, "floor": 1}]


@pytest.mark.parametrize(
    ("current_type", "next_type", "instruction"),
    [
        ("staircase", "waypoint", "Take the stairs from floor 1 to floor 2."),
        ("waypoint", "staircase", "Take the stairs from floor 1 to floor 2."),
        ("elevator", "elevator", "Take elevator E1 to floor 2."),
        ("waypoint", "elevator", "Move from floor 1 to floor 2."),
    ],
)
def test_navigation_describes_floor_transitions(
    monkeypatch, current_type, next_type, instruction
):
    nodes = [
        node("start", floor=1, node_type=current_type),
        node("end", floor=2, node_type=next_type),
    ]
    edges = [
        {
            "source": "start",
            "target": "end",
            "weight": 1,
            "instruction": "Take elevator E1 to floor 2.",
        }
    ]
    floors = {
        "BLDG": {
            "1": {"width_feet": 100, "height_feet": 80},
            "2": {"width_feet": 100, "height_feet": 80},
        }
    }
    monkeypatch.setattr(
        navigation, "_load_map_facts", lambda: facts(nodes, edges, floors)
    )

    outcome = navigation.navigate(select())

    assert outcome["directions"] == [instruction]
    assert outcome["traversed_floors"] == [1, 2]
    assert outcome["map"]["status"] == "unavailable"
    assert "spanning multiple floors" in outcome["map"]["message"]


def test_navigation_reports_missing_route_without_a_string_or_dict_convention(
    monkeypatch,
):
    monkeypatch.setattr(
        navigation,
        "_load_map_facts",
        lambda: facts([node("start"), node("end", node_type="room")]),
    )

    outcome = navigation.navigate(select())

    assert outcome["status"] == "error"
    assert outcome["directions"] == []
    assert "No route could be found" in outcome["error"]


def test_navigation_turns_data_failures_into_an_outcome(monkeypatch):
    monkeypatch.setattr(
        navigation,
        "_load_map_facts",
        lambda: (_ for _ in ()).throw(RuntimeError("data is unavailable")),
    )

    outcome = navigation.navigate(select())

    assert outcome["status"] == "error"
    assert outcome["error"] == "data is unavailable"
    assert outcome["options"] == {"entrances": [], "classrooms": []}


def test_navigation_reports_missing_floor_data(monkeypatch):
    nodes = [node("start"), node("end", node_type="room")]
    edges = [
        {"source": "start", "target": "end", "weight": 1, "instruction": "Arrive."}
    ]
    monkeypatch.setattr(navigation, "_load_map_facts", lambda: facts(nodes, edges, {}))

    outcome = navigation.navigate(select())

    assert outcome["status"] == "error"
    assert outcome["error"] == "No floor data for BLDG floor 1"


def test_graph_cache_is_built_lazily_and_can_be_replaced():
    nodes = [node("start"), node("end")]
    edge = {"source": "start", "target": "end", "weight": 1, "instruction": "Go."}

    first = navigation._get_graph(nodes, [edge])
    second = navigation._get_graph([], [])
    navigation._graph = None
    replacement = navigation._get_graph([], [])

    assert isinstance(first, nx.DiGraph)
    assert second is first
    assert replacement is not first
    assert replacement.number_of_nodes() == 0


def test_json_loader_uses_the_module_data_directory(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    for filename, value in (
        ("nodes.json", [{"id": "a"}]),
        ("edges.json", []),
        ("floors.json", {"BLDG": {}}),
    ):
        (data_dir / filename).write_text(json.dumps(value), encoding="utf-8")
    monkeypatch.setattr(navigation, "_DATA_DIR", data_dir)

    assert navigation._load_map_facts() == ([{"id": "a"}], [], {"BLDG": {}})


def test_logic_exports_only_the_deep_navigation_interface():
    assert logic.__all__ == ["navigate"]
    assert logic.navigate is navigation.navigate
