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
    user_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/sessions?user_id={user_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid authentication token"

def test_list_sessions_invalid_auth():
    user_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"/api/sessions?user_id={user_id}",
        headers={"Authorization": "InvalidToken123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid authentication token"
