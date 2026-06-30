import pytest
from fastapi.testclient import TestClient
from api import app
from unittest.mock import patch, AsyncMock, MagicMock
import os

os.environ["SUPABASE_URL"] = "http://test"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test"
os.environ["SUPABASE_ANON_KEY"] = "test"

client = TestClient(app)

def test_list_sessions_unauthorized():
    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401

@patch('database.client.get_user_client')
@patch('database.repositories.session_repository.SessionRepository')
def test_list_sessions_authorized(mock_repo_class, mock_get_client):
    mock_repo_instance = MagicMock()
    mock_repo_instance.list_by_user = AsyncMock(return_value=[])
    mock_repo_class.return_value = mock_repo_instance

    mock_client = AsyncMock()
    mock_get_client.return_value = mock_client

    response = client.get("/api/sessions?user_id=123e4567-e89b-12d3-a456-426614174000", headers={"Authorization": "Bearer test-jwt-token"})
    assert response.status_code == 404
    mock_get_client.assert_called_once_with("test-jwt-token")
