from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v1_ping():
    response = client.get("/v1/system/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "api_version": "v1"}
