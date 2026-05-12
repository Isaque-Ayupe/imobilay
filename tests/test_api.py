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
    import uuid
    user_id = str(uuid.uuid4())
    response = client.get(f"/api/sessions?user_id={user_id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid Authorization header"
