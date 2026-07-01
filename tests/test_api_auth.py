from fastapi.testclient import TestClient
from api import app
import os

client = TestClient(app)

def test_list_sessions_unauthorized_prod():
    os.environ["ENVIRONMENT"] = "production"
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid authorization header."
    os.environ.pop("ENVIRONMENT", None)

def test_list_sessions_unauthorized_dev():
    os.environ["ENVIRONMENT"] = "development"
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code != 401
    os.environ.pop("ENVIRONMENT", None)
