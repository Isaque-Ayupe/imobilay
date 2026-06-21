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
    # Attempting to fetch sessions without an Authorization header should return a 422 Unprocessable Entity
    # because fastapi.Header(...) makes it a required parameter.
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/api/sessions?user_id={user_id}")
    assert response.status_code == 422
    data = response.json()
    # Confirm it's the missing authorization header
    assert any("authorization" in err.get("loc", []) for err in data["detail"])

def test_list_sessions_invalid_auth_header():
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    # Provide a header that does not start with "Bearer "
    response = client.get(
        f"/api/sessions?user_id={user_id}",
        headers={"Authorization": "Basic something"}
    )
    assert response.status_code == 401
    assert "Invalid authorization header format" in response.json()["detail"]
