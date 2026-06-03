from fastapi.testclient import TestClient
from api import app
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_health_check_supabase_fail():
    response = client.get("/api/health")
    # without env vars set, it should fail
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert data["detail"]["dependencies"]["supabase"] == "error"

def test_list_sessions_missing_auth():
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    # missing header returns 422 Unprocessable Entity by FastAPI
    assert response.status_code == 422

@patch("database.client.get_user_client", new_callable=AsyncMock)
@patch("database.repositories.session_repository.SessionRepository.list_by_user", new_callable=AsyncMock)
def test_list_sessions_success_with_auth(mock_list_by_user, mock_get_user_client):
    mock_list_by_user.return_value = [] # no sessions found to return 404

    response = client.get(
        "/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": "Bearer some-fake-jwt-token"}
    )

    assert mock_get_user_client.call_count == 1
    assert mock_get_user_client.call_args[0][0] == "some-fake-jwt-token"

    assert mock_list_by_user.call_count == 1
    assert mock_list_by_user.call_args[0][0] == "123e4567-e89b-12d3-a456-426614174000"

    # Empty list triggers 404 in endpoint
    assert response.status_code == 404
    assert response.json()["detail"] == "No sessions found for this user."
