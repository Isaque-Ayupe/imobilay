from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_sessions_endpoint_requires_auth():
    # Attempting to access sessions without authorization should fail
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Missing or invalid Authorization header."
