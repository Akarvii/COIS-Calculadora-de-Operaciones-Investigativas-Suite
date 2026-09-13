import pytest
from starlette.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_examples_endpoint():
    response = client.get("/api/examples")
    assert response.status_code == 200
    examples = response.json()
    assert len(examples) >= 4


def test_api_standard_solve():
    payload = {
        "objective_type": "MAXIMIZE",
        "c": [3, 5],
        "A": [
            [1, 0],
            [0, 2],
            [3, 2]
        ],
        "constraint_types": ["<=", "<=", "<="],
        "b": [4, 12, 18]
    }
    response = client.post("/api/solve/standard", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPTIMAL"
    assert data["optimal_value"]["fraction"] == "36"
    assert data["solution"]["x1"]["fraction"] == "2"
    assert data["solution"]["x2"]["fraction"] == "6"
    assert len(data["tabular_iterations"]) > 0


def test_api_revised_solve():
    payload = {
        "objective_type": "MAXIMIZE",
        "c": [3, 5],
        "A": [
            [1, 0],
            [0, 2],
            [3, 2]
        ],
        "constraint_types": ["<=", "<=", "<="],
        "b": [4, 12, 18]
    }
    response = client.post("/api/solve/revised", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPTIMAL"
    assert data["optimal_value"]["fraction"] == "36"
    assert len(data["revised_iterations"]) > 0
    # Check that B_inv matrix is returned in steps
    step0 = data["revised_iterations"][0]
    assert "B_inv" in step0
    assert "pi_multipliers" in step0


def test_api_compare_endpoint():
    payload = {
        "objective_type": "MAXIMIZE",
        "c": [2, 3],
        "A": [
            [1, 2],
            [3, 2]
        ],
        "constraint_types": ["<=", "<="],
        "b": [8, 14]
    }
    response = client.post("/api/solve/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_consistent"] is True
    assert data["standard_result"]["optimal_value"]["fraction"] == "27/2"
    assert data["revised_result"]["optimal_value"]["fraction"] == "27/2"


def test_api_validation_error_handling():
    # Sending invalid data (dimension mismatch) should return structured HTTP 422, not crash
    payload = {
        "objective_type": "MAXIMIZE",
        "c": [1, 2, 3],
        "A": [[1, 2]],
        "constraint_types": ["<="],
        "b": [10]
    }
    response = client.post("/api/solve/standard", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "VALIDATION_ERROR"
    assert "message" in data
