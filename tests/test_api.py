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
    dummy_uuid = str(uuid.uuid4())
    response = client.get(f"/api/sessions?user_id={dummy_uuid}")
    assert response.status_code == 401
    assert "Missing or invalid Authorization header" in response.json()["detail"]

def test_list_sessions_invalid_auth_header_format():
    import uuid
    dummy_uuid = str(uuid.uuid4())
    response = client.get(
        f"/api/sessions?user_id={dummy_uuid}",
        headers={"Authorization": "InvalidFormatToken"}
    )
    assert response.status_code == 401
    assert "Missing or invalid Authorization header" in response.json()["detail"]
