from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_list_sessions_missing_auth():
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid Authorization header."


def test_list_sessions_invalid_auth_format():
    response = client.get(
        "/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": "InvalidTokenFormat"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid Authorization header."


def test_health_check_supabase_fail():
    response = client.get("/api/health")
    # without env vars set, it should fail
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert data["detail"]["dependencies"]["supabase"] == "error"
