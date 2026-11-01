from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from k_cher.api import app
from k_cher.db import get_db


def test_create_add_calculation(client):
    response = client.post("/calculations", json={"operation": "add", "a": 2, "b": 3})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["operation"] == "add"
    assert body["result"] == 5.0
    assert "created_at" in body


def test_create_divide_calculation(client):
    response = client.post(
        "/calculations", json={"operation": "divide", "a": 9, "b": 4}
    )

    assert response.status_code == 201
    assert response.json()["result"] == 2.25


def test_divide_by_zero_returns_400_and_is_not_saved(client):
    response = client.post(
        "/calculations", json={"operation": "divide", "a": 1, "b": 0}
    )

    assert response.status_code == 400
    assert client.get("/calculations").json() == []


def test_result_out_of_range_returns_400(client):
    response = client.post(
        "/calculations", json={"operation": "add", "a": 1.7e308, "b": 1.7e308}
    )

    assert response.status_code == 400


def test_unknown_operation_returns_422(client):
    response = client.post("/calculations", json={"operation": "pow", "a": 1, "b": 2})

    assert response.status_code == 422


def test_get_calculation_by_id(client):
    created = client.post(
        "/calculations", json={"operation": "add", "a": 1, "b": 1}
    ).json()

    response = client.get(f"/calculations/{created['id']}")

    assert response.status_code == 200
    assert response.json()["result"] == 2.0


def test_get_missing_calculation_returns_404(client):
    assert client.get("/calculations/999").status_code == 404


def test_invalid_id_returns_422(client):
    assert client.get("/calculations/0").status_code == 422


def test_list_returns_newest_first_and_respects_limit(client):
    for a in (1, 2, 3):
        client.post("/calculations", json={"operation": "add", "a": a, "b": 0})

    items = client.get("/calculations").json()
    limited = client.get("/calculations", params={"limit": 2}).json()

    assert [item["a"] for item in items] == [3, 2, 1]
    assert len(limited) == 2
    assert client.get("/calculations", params={"limit": 0}).status_code == 422


def test_delete_calculation(client):
    created = client.post(
        "/calculations", json={"operation": "add", "a": 1, "b": 2}
    ).json()

    assert client.delete(f"/calculations/{created['id']}").status_code == 204
    assert client.get(f"/calculations/{created['id']}").status_code == 404
    assert client.delete(f"/calculations/{created['id']}").status_code == 404


def test_ready_returns_ok(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_returns_503_when_database_is_down(client):
    class BrokenSession:
        def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception("down"))

    app.dependency_overrides[get_db] = lambda: BrokenSession()

    assert client.get("/ready").status_code == 503


def test_database_not_configured_returns_503():
    response = TestClient(app).get("/calculations")

    assert response.status_code == 503
    assert "DB_HOST" in response.json()["detail"]


def test_health_does_not_need_database():
    assert TestClient(app).get("/health").json() == {"status": "ok"}
