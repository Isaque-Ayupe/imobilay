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

def test_list_sessions_missing_authorization_header():
    import uuid
    user_id = str(uuid.uuid4())
    response = client.get(f"/api/sessions?user_id={user_id}")
    # Missing required Header parameter returns 422 Unprocessable Entity
    assert response.status_code == 422

def test_list_sessions_invalid_authorization_format():
    import uuid
    user_id = str(uuid.uuid4())
    response = client.get(
        f"/api/sessions?user_id={user_id}",
        headers={"Authorization": "InvalidToken123"}
    )
    # Invalid format (not starting with Bearer ) returns 401
    assert response.status_code == 401
    assert "Invalid authorization header format" in response.json()["detail"]
