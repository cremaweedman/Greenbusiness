from fastapi.testclient import TestClient

from app.errors import AppError
from app.main import app


@app.get("/__test__/intentional-error")
async def intentional_error():
    raise AppError(
        "INTENTIONAL_TEST_ERROR",
        "Intentional test failure.",
        status_code=409,
        details={"reason": "test"},
    )


client = TestClient(app)


def test_canonical_error_envelope():
    response = client.get(
        "/__test__/intentional-error",
        headers={"X-Request-ID": "request-123"},
    )
    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "INTENTIONAL_TEST_ERROR",
            "message": "Intentional test failure.",
            "details": {"reason": "test"},
            "request_id": "request-123",
        }
    }
