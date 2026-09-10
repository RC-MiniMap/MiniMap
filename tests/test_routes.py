import json
import re
from unittest.mock import Mock

import pytest

from app import logic, routes
from app.logic import navigation

OPTIONS = {
    "entrances": [{"id": "NPB_5_E1", "name": "5.E1 elevator"}],
    "classrooms": [{"id": "NPB_5_154", "name": "5.154"}],
}


def make_outcome(
    *,
    status="idle",
    error=None,
    directions=None,
    map_status="idle",
    map_data=None,
    map_message=None,
):
    return {
        "status": status,
        "error": error,
        "directions": directions or [],
        "traversed_floors": [],
        "map": {"status": map_status, "data": map_data, "message": map_message},
        "options": OPTIONS,
    }


@pytest.fixture(autouse=True)
def stub_navigation(monkeypatch):
    monkeypatch.setattr(routes, "navigate", lambda selection=None: make_outcome())


def embedded_json(body, variable):
    match = re.search(
        rf"(?:window\.)?{re.escape(variable)}\s*=\s*(?P<value>.*?);",
        body,
        flags=re.DOTALL,
    )
    assert match, f"{variable} was not embedded in the response"
    return json.loads(match.group("value"))


def test_index_passes_an_empty_request_to_navigation_and_renders_options(
    client, monkeypatch
):
    navigate = Mock(return_value=make_outcome())
    monkeypatch.setattr(routes, "navigate", navigate)

    response = client.get("/")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert '<select id="entrance" name="entrance">' in body
    assert 'value="NPB_5_E1">5.E1 elevator' in body
    assert 'value="NPB_5_154">5.154' in body
    assert "Map will appear here after you select directions" in body
    assert "window.routeMap" not in body
    navigate.assert_called_once_with()


def test_directions_passes_the_form_directly_to_navigation(client, monkeypatch):
    outcome = make_outcome(
        status="success",
        directions=["Leave the elevator.", "Turn left."],
        map_status="ready",
        map_data={
            "coordinates": [
                {"x": 1, "y": 2, "floor": 4},
                {"x": 3.5, "y": -6, "floor": 4},
            ],
            "bounds": {"width": 300, "height": 60},
        },
    )
    navigate = Mock(return_value=outcome)
    monkeypatch.setattr(routes, "navigate", navigate)

    response = client.post(
        "/directions",
        data={"entrance": "NPB_5_E1", "classroom": "NPB_5_154"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert embedded_json(body, "directionSteps") == outcome["directions"]
    assert embedded_json(body, "routeMap") == outcome["map"]["data"]
    assert "/static/js/directions.js" in body
    assert "/static/js/map.js" in body
    selection = navigate.call_args.args[0]
    assert selection["entrance"] == "NPB_5_E1"
    assert selection["classroom"] == "NPB_5_154"


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            "Missing entrance or classroom parameter",
            "Missing entrance or classroom parameter",
        ),
        ("data is unavailable", "data is unavailable"),
        (
            "No route could be found between the selected entrance and destination.",
            "No route could be found",
        ),
    ],
)
def test_directions_renders_navigation_errors(client, monkeypatch, error, expected):
    monkeypatch.setattr(
        routes, "navigate", Mock(return_value=make_outcome(status="error", error=error))
    )

    response = client.post("/directions", data={})

    assert response.status_code == 200
    assert expected in response.get_data(as_text=True)


def test_directions_renders_map_unavailability_from_outcome(client, monkeypatch):
    message = "Map preview is unavailable for routes spanning multiple floors."
    monkeypatch.setattr(
        routes,
        "navigate",
        Mock(
            return_value=make_outcome(
                status="success",
                directions=["Take the elevator."],
                map_status="unavailable",
                map_message=message,
            )
        ),
    )

    response = client.post("/directions", data={})
    body = response.get_data(as_text=True)

    assert message in body
    assert "window.routeMap" not in body


def test_live_navigation_uses_canonical_data(client, monkeypatch):
    monkeypatch.setattr(routes, "navigate", logic.navigate)
    navigation._graph = None

    response = client.post(
        "/directions",
        data={"entrance": "NPB_5_E1", "classroom": "NPB_4_440"},
    )

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Take elevator E1 to floor 4." in body
    assert "Map preview is unavailable for routes spanning multiple floors." in body
    assert "window.routeMap" not in body


def test_directions_only_accepts_post(client):
    assert client.get("/directions").status_code == 405


def test_api_test_returns_the_navigation_outcome(client, monkeypatch):
    expected = make_outcome(status="success", directions=["Test route"])
    navigate = Mock(return_value=expected)
    monkeypatch.setattr(routes, "navigate", navigate)

    response = client.get("/api/test")

    assert response.status_code == 200
    assert response.get_json() == expected
    navigate.assert_called_once_with({"entrance": "NPB_5_E1", "classroom": "NPB_5_154"})


def test_unknown_url_returns_not_found(client):
    assert client.get("/does-not-exist").status_code == 404


@pytest.mark.parametrize(
    ("path", "mimetype"),
    [
        ("/static/css/styles.css", "text/css"),
        ("/static/js/directions.js", "text/javascript"),
        ("/static/js/map.js", "text/javascript"),
    ],
)
def test_static_assets_are_served(client, path, mimetype):
    response = client.get(path)

    assert response.status_code == 200
    assert response.mimetype == mimetype
    assert response.data
