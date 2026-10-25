from fastapi.testclient import TestClient

from k_cher import __version__
from k_cher.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}


def test_hello():
    response = client.get("/hello/Kate")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Kate!"}


def test_add():
    response = client.get("/add", params={"a": 2, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 5.0}


def test_divide():
    response = client.get("/divide", params={"a": 6, "b": 3})
    assert response.status_code == 200
    assert response.json() == {"result": 2.0}


def test_divide_by_zero():
    response = client.get("/divide", params={"a": 1, "b": 0})
    assert response.status_code == 400
