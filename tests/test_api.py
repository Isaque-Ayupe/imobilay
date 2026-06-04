from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health_check_supabase_fail():
    response = client.get("/api/health")
    # without env vars set, it should fail
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert data["detail"]["dependencies"]["supabase"] == "error"

def test_list_sessions_missing_auth():
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    # Should fail with 422 Unprocessable Entity because 'authorization' header is required by FastAPI
    assert response.status_code == 422

def test_list_sessions_invalid_auth_format():
    response = client.get(
        "/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == 401
    assert "Invalid authorization header format" in response.json()["detail"]

from unittest.mock import patch, MagicMock

@patch("database.client.get_user_client")
def test_list_sessions_valid_auth(mock_get_user_client):
    # This is a basic test to ensure we reach the logic with valid auth header
    # Since we can't easily mock the entire async DB flow in a simple test without proper pytest-asyncio fixtures,
    # we just verify the auth header is accepted and it passes to the UUID validation or client instantiation
    response = client.get(
        "/api/sessions?user_id=invalid-uuid",
        headers={"Authorization": "Bearer token123"}
    )
    # Should fail at UUID validation, meaning auth passed
    assert response.status_code == 400
    assert "Invalid user_id format" in response.json()["detail"]
