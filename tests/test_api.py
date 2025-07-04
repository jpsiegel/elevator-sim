from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_post_simulation():
    """
    Test that the /simulation endpoint correctly creates a simulation record.
    Checks for status 200 and presence of required fields in the response.
    """
    response = client.post("/simulation", json={
        "wait_time": 1.0,
        "elevator_speed": 1.0,
        "expo_lambda": 0.1,
        "start_datetime": "2025-06-29T00:00:00",
        "duration": 100,
        "base_floor": 1,
        "base_floor_weight": 5,
        "floor_min": 1,
        "floor_max": 5,
        "random_seed": 42
    })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["elevator_speed"] == 1.0
    global simulation_id
    simulation_id = data["id"]  # used in subsequent tests


def test_post_elevator_request():
    """
    Test that the /elevator_request endpoint correctly stores a request snapshot.
    Uses the simulation ID from the previous test. Verifies basic structure.
    """
    payload = {
        "simulation_id": simulation_id,
        "current_floor": 3,
        "last_floor": 2,
        "time_idle": 5.0,
        "timestamp": "2025-06-29T00:01:00",
        "floor_demand_histogram": [1, 2, 3, 0, 0],
        "hot_floor_last_30s": 2,
        "requests_entropy": 1.5,
        "mean_requested_floor": 2.5,
        "distance_to_center_of_mass": 0.5,
        "next_floor_requested": 1
    }
    response = client.post("/elevator_request", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["current_floor"] == 3
    global request_id
    request_id = data["id"]


def test_get_requests_by_simulation():
    """
    Test that the /elevator_request/{sim_id} endpoint returns a list of requests.
    Verifies the previously posted request is included in the list.
    """
    response = client.get(f"/elevator_request/{simulation_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(req["id"] == request_id for req in data)
