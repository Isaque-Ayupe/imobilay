from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_list_sessions_missing_auth():
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid authentication token."}

def test_list_sessions_invalid_auth_format():
    response = client.get(
        "/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": "InvalidTokenFormat 1234"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid authentication token."}
