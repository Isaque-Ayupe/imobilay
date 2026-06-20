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
    import uuid
    user_id = str(uuid.uuid4())
    # Should return 422 because authorization header is required
    response = client.get(f"/api/sessions?user_id={user_id}")
    assert response.status_code == 422

def test_list_sessions_invalid_auth_header():
    import uuid
    user_id = str(uuid.uuid4())
    # Should return 401 because 'Bearer ' prefix is missing
    response = client.get(
        f"/api/sessions?user_id={user_id}",
        headers={"Authorization": "invalid_token_format"}
    )
    assert response.status_code == 401
    assert "Invalid authorization header format" in response.json()["detail"]
