from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status":"ok"}

def test_request_id_is_returned():
    response = client.get("/health/live", headers={"X-Request-ID":"test-id"})
    assert response.headers["X-Request-ID"] == "test-id"
