import pytest

from controller.user import user_service
from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter


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

    def mock_check_for_username(self, username):
        return False

    mocker.patch('dao.user.UserDao.check_for_email', mock_check_for_email)
    mocker.patch('dao.user.UserDao.check_for_username', mock_check_for_username)
    # Act and  # Assert
    with pytest.raises(Forbidden):
        user_service.add_user('jcad1', 'Password123!!', 'a@a.ca')


def test_add_user_valid_data(mocker):
    # Arrange
    def mock_add_user(self, user):
        return 'User successfully added!'

    mocker.patch('dao.user.UserDao.add_user', mock_add_user)
    # Actual
    actual = user_service.add_user('validUser', 'Password123!!', 'z@a.ca')
    expected = 'User successfully added!'
    # Assert
    assert actual == expected


def test_invalid_username_format_length_3():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jca', 'Password123!!', 'a@a.ca')


def test_invalid_username_format_length_31():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('a111111111111111111111111111111', 'Password123!!', 'a@a.ca')


def test_invalid_username_format_non_alphanumeric():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jca@', 'Password123!!', 'a@a.ca')


def test_invalid_username_format_empty_string():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('', 'Password123!!', 'a@a.ca')


def test_invalid_email_format_empty_string():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'Password123!!', '')


def test_invalid_email_format():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'Password123!!', 'aa.ca')


def test_invalid_password_format_empty_string():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', '', 'a@a.ca')


def test_invalid_password_format_length_21():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'Password123!.........', 'a@a.ca')


def test_invalid_password_format_length_7():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'Passw3!', 'a@a.ca')


def test_invalid_password_format_Invalid_special_character():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'Password123{.......', 'a@a.ca')


def test_invalid_password_format_missing_alphabetic_lowercase():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'P123456!', 'a@a.ca')


def test_invalid_password_format_missing_alphabetic_uppercase():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'p123456!', 'a@a.ca')


def test_invalid_password_format_missing_special_character():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'P123456p', 'a@a.ca')


def test_invalid_password_format_missing_numeric():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter):
        user_service.add_user('jcad1', 'Pabcderf!', 'a@a.ca')


