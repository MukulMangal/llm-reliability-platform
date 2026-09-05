from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import register_exception_handlers


def test_global_exception_handler():
    app = FastAPI()

    register_exception_handlers(app)

    @app.get("/test-error")
    def test_error():
        raise RuntimeError("Something went wrong")

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.get("/test-error")

    assert response.status_code == 500

    assert response.json() == {
        "error": "internal_server_error",
        "detail": "Internal Server Error",
    }