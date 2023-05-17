import pytest

from controller.user import user_service
from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from model.user import User


def test_check_for_username_existing(mocker):
    # Arrange
    def mock_check_for_username(self, username):
        return True

    mocker.patch('dao.user.UserDao.check_for_username', mock_check_for_username)
    # Act and  # Assert
    with pytest.raises(Forbidden) as e:
        user_service.add_user('jcad1', 'Password123!!', 'a@a.ca')
    assert str(e.value) == 'This username is already in use! Please try again.'


def test_check_for_email_existing(mocker):
    # Arrange
    def mock_check_for_email(self, email):
        return True

    def mock_check_for_username(self, username):
        return False

    mocker.patch('dao.user.UserDao.check_for_email', mock_check_for_email)
    mocker.patch('dao.user.UserDao.check_for_username', mock_check_for_username)
    # Act and  # Assert
    with pytest.raises(Forbidden) as e:
        user_service.add_user('jcad1', 'Password123!!', 'a@a.ca')
    assert str(e.value) == 'This email is already in use! Please sign into your existing account.'


def test_add_user_valid_data(mocker):
    # Arrange
    def mock_add_user(self, user):
        return 'User successfully added!'

    mocker.patch('dao.user.UserDao.add_user', mock_add_user)
    # Act
    actual = user_service.add_user('validUser', 'Password123!!', 'z@a.ca')
    expected = 'User successfully added!'
    # Assert
    assert actual == expected


def test_update_user_invalid_current_password(mocker):
    # Arrange
    def mock_get_user_by_id(self, username):
        return User(1, 'jcad1', '$2b$12$kcvn4uWQAKdu.ZJ1Mv4KV./XBKlIrjTiNkcARUxBZMdCuUC.JixoG', 'a@a.ca')

    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)
    # Act and  # Assert
    with pytest.raises(Forbidden) as e:
        user_service.update_user('1', 'Password123!!', 'Password123!!2', 'a@a.ca')
    assert str(e.value) == 'Invalid password for this account!'


def test_update_user_valid_current_password_invalid_email(mocker):
    # Arrange
    def mock_get_user_by_id(self, username):
        return User(1, 'jcad1', '$2b$12$kcvn4uWQAKdu.ZJ1Mv4KV./XBKlIrjTiNkcARUxBZMdCuUC.JixoG', 'a@a.ca')

    def mock_check_for_email(self, email):
        return True

    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)
    mocker.patch('dao.user.UserDao.check_for_email', mock_check_for_email)
    # Act and  # Assert
    with pytest.raises(Forbidden) as e:
        user_service.update_user(1, 'Password123!!2', 'Password123!!', 'a@a.ca')
    assert str(e.value) == 'Please sign into your existing account.'


def test_update_user_valid_current_password_valid_email(mocker):
    # Arrange
    def mock_get_user_by_id(self, username):
        return User(1, 'jcad1', '$2b$12$kcvn4uWQAKdu.ZJ1Mv4KV./XBKlIrjTiNkcARUxBZMdCuUC.JixoG', 'a@a.ca')

    def mock_check_for_email(self, email):
        return False

    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)
    mocker.patch('dao.user.UserDao.check_for_email', mock_check_for_email)
    # Act
    actual = user_service.update_user(1, 'Password123!!2', 'Password123!!', 'a1234@a.ca')
    expected = 'Email successfully updated!'
    # Assert
    assert actual == expected


def test_update_user_invalid_current_password_no_email(mocker):
    # Arrange
    def mock_get_user_by_id(self, username):
        return User(1, 'jcad1', '$2b$12$kcvn4uWQAKdu.ZJ1Mv4KV./XBKlIrjTiNkcARUxBZMdCuUC.JixoG', 'a@a.ca')

    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)

    # Act and  # Assert
    with pytest.raises(Forbidden) as e:
        user_service.update_user(1, 'Password123!!', 'Password123!!', None)
    assert str(e.value) == 'Invalid password for this account!'


def test_update_user_valid_current_password_no_email(mocker):
    # Arrange
    def mock_get_user_by_id(self, username):
        return User(1, 'jcad1', '$2b$12$kcvn4uWQAKdu.ZJ1Mv4KV./XBKlIrjTiNkcARUxBZMdCuUC.JixoG', 'a@a.ca')

    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)

    # Act
    actual = user_service.update_user(1, 'Password123!!2', 'Password123!!', None)
    expected = 'Password successfully updated!'
    # Assert
    assert actual == expected


# input_validation_helper tests

def test_invalid_username_format_length_3():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jca', 'Password123!!', 'a@a.ca')
    assert str(e.value) == 'Usernames must have at least 4 alphanumeric characters'


def test_invalid_username_format_length_31():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('a111111111111111111111111111111', 'Password123!!', 'a@a.ca')
    assert str(e.value) == 'Usernames are limited to 30 alphanumeric characters '


def test_invalid_username_format_non_alphanumeric():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jca@', 'Password123!!', 'a@a.ca')
    assert str(e.value) == 'Usernames must have only alphanumeric characters'


def test_invalid_username_format_empty_string():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('', 'Password123!!', 'a@a.ca')
    assert str(e.value) == 'Usernames cannot be blank'


def test_invalid_email_format_empty_string():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'Password123!!', '')
    assert str(e.value) == 'Email cannot be blank'


def test_invalid_email_format():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'Password123!!', 'aa.ca')
    assert str(e.value) == 'Accepted email address format is: username@domain.domain_type'


def test_invalid_password_format_empty_string():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', '', 'a@a.ca')
    assert str(e.value) == 'password cannot be blank'


def test_invalid_password_format_length_21():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'Password123!.........', 'a@a.ca')
    assert str(e.value) == 'Accepted password length is between 8 and 20 characters inclusive'


def test_invalid_password_format_length_7():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'Passw3!', 'a@a.ca')
    assert str(e.value) == 'Accepted password length is between 8 and 20 characters inclusive'


def test_invalid_password_format_invalid_special_character():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'Password123{.......', 'a@a.ca')
    assert str(e.value) == 'Password must contain only alphanumeric and special characters only from this set (' \
                           '!@#$%^&*)'


def test_invalid_password_format_missing_alphabetic_lowercase():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'P123456!', 'a@a.ca')
    assert str(e.value) == 'Password must have at least 1 lowercase character'


def test_invalid_password_format_missing_alphabetic_uppercase():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'p123456!', 'a@a.ca')
    assert str(e.value) == 'Password must have at least 1 uppercase character'


def test_invalid_password_format_missing_special_character():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'P123456p', 'a@a.ca')
    assert str(e.value) == 'Password must have at least 1 special (!@#$%^&*) character'


def test_invalid_password_format_missing_numeric():
    # Arrange
    # Act and  # Assert
    with pytest.raises(InvalidParameter) as e:
        user_service.add_user('jcad1', 'Pabcderf!', 'a@a.ca')
    assert str(e.value) == 'Password must have at least 1 numeric character'
