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
    valid_uuid = str(uuid.uuid4())
    # Should return 422 Unprocessable Entity when required Header is missing in FastAPI
    response = client.get(f"/api/sessions?user_id={valid_uuid}")
    assert response.status_code == 422

def test_list_sessions_invalid_auth_header():
    import uuid
    valid_uuid = str(uuid.uuid4())
    response = client.get(
        f"/api/sessions?user_id={valid_uuid}",
        headers={"Authorization": "InvalidToken"}
    )
    # Should return 401 Unauthorized for invalid token format
    assert response.status_code == 401
    assert "Invalid authorization header format" in response.json()["detail"]
