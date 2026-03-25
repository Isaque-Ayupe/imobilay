import pytest
from unittest.mock import MagicMock
from src.user_service import UserService

def test_get_user_success():
    db_mock = MagicMock()
    db_mock.find_user.return_value = {"id": "123", "name": "John Doe"}

    service = UserService(db_mock)
    user = service.get_user("123")

    assert user == {"id": "123", "name": "John Doe"}
    db_mock.find_user.assert_called_once_with("123")

def test_get_user_empty_string():
    db_mock = MagicMock()
    service = UserService(db_mock)

    with pytest.raises(ValueError) as excinfo:
        service.get_user("")

    assert "user_id must be provided" in str(excinfo.value)
    db_mock.find_user.assert_not_called()

def test_get_user_none():
    db_mock = MagicMock()
    service = UserService(db_mock)

    with pytest.raises(ValueError) as excinfo:
        service.get_user(None)

    assert "user_id must be provided" in str(excinfo.value)
    db_mock.find_user.assert_not_called()
