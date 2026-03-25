import pytest
from unittest.mock import MagicMock
from src.user_service import UserService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def user_service(mock_db):
    return UserService(mock_db)

def test_get_user_success(user_service, mock_db):
    # Arrange
    user_id = "user123"
    expected_user = {"id": user_id, "username": "testuser", "email": "test@example.com"}
    mock_db.find_user.return_value = expected_user

    # Act
    result = user_service.get_user(user_id)

    # Assert
    mock_db.find_user.assert_called_once_with(user_id)
    assert result == expected_user

def test_get_user_empty_id(user_service, mock_db):
    # Arrange
    user_id = ""

    # Act & Assert
    with pytest.raises(ValueError, match="user_id must be provided"):
        user_service.get_user(user_id)

    mock_db.find_user.assert_not_called()

def test_get_user_none_id(user_service, mock_db):
    # Arrange
    user_id = None

    # Act & Assert
    with pytest.raises(ValueError, match="user_id must be provided"):
        user_service.get_user(user_id)

    mock_db.find_user.assert_not_called()

def test_create_user(user_service, mock_db):
    # Arrange
    username = "newuser"
    email = "newuser@example.com"
    expected_user = {"username": username, "email": email}

    # Act
    result = user_service.create_user(username, email)

    # Assert
    mock_db.save.assert_called_once_with(expected_user)
    assert result == expected_user
