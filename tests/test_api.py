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

def test_list_sessions_missing_auth_header():
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    # Missing required header should return 422 Unprocessable Entity in FastAPI
    assert response.status_code == 422

def test_list_sessions_invalid_auth_header():
    response = client.get(
        "/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": "InvalidToken123"}
    )
    # Invalid bearer format should return 401 Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid authorization header."
