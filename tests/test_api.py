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

from unittest.mock import patch, MagicMock
from datetime import datetime

def test_list_sessions_missing_header():
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    # Missing required 'authorization' header
    assert response.status_code == 422

def test_list_sessions_invalid_header_format():
    response = client.get(
        "/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": "InvalidTokenFormat"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authorization header format."

import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
@patch("database.client.get_user_client", new_callable=AsyncMock)
@patch("database.repositories.session_repository.SessionRepository")
async def test_list_sessions_success(mock_repo_cls, mock_get_client):
    from database.repositories.session_repository import SessionRecord
    import uuid

    # Mock the returned records
    mock_repo_instance = mock_repo_cls.return_value
    mock_record = SessionRecord(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Test Session",
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    mock_repo_instance.list_by_user = AsyncMock(return_value=[mock_record])

    # Mock the client
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    # Run the request via TestClient
    response = client.get(
        "/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": "Bearer fake_jwt_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Session"

    # Verify get_user_client was called with correct JWT
    mock_get_client.assert_called_once_with("fake_jwt_token")
