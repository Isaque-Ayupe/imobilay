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
    dummy_user_id = str(uuid.uuid4())
    # Sending request without Authorization header
    response = client.get(f"/api/sessions?user_id={dummy_user_id}")
    # fastapi.Header returns 422 if missing when it is required, but we made it default=None
    # and explicitly check and return 401 if not valid.
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Missing or invalid authentication token."
