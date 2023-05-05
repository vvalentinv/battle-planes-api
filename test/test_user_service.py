import pytest

from controller.user import user_service
from exception.forbidden import Forbidden


def test_check_for_username_existing(mocker):
    # Arrange
    def mock_check_for_username(self, username):
        return True

    mocker.patch('dao.user.UserDao.check_for_username', mock_check_for_username)
    # Act and  # Assert
    with pytest.raises(Forbidden):
        user_service.add_user('jcad1', 'Password123!!', 'a@a.ca')


def test_check_for_email_existing(mocker):
    # Arrange
    def mock_check_for_email(self, email):
        return True

    mocker.patch('dao.user.UserDao.check_for_email', mock_check_for_email)
    # Act and  # Assert
    with pytest.raises(Forbidden):
        user_service.add_user('jcad1', 'Password123!!', 'a@a.ca')
