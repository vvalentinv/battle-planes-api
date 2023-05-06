import pytest

from controller.battle import battle_service
from exception.invalid_parameter import InvalidParameter
from model.user import User


def test_add_battle_valid_params(mocker):
    # Arrange
    def mock_get_user_by_id(self, user_id):
        return User(1, 'jcad1', 'some_password_hash', 'some_email')

    def mock_is_engaged(self, user_id):
        return False

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)
    # Act
    actual = battle_service.add_battle(1, [1, 2, 3], 3, 10, 10)
    expected = 'You have set your defense and waiting for a challenger!'
    # Assert
    assert actual == expected


def test_add_battle_invalid_int():
    # Act and # Assert
    with pytest.raises(InvalidParameter):
        battle_service.add_battle(1, [1, 2, 3], '2s', 10, 10)


def test_add_plane_to_battle_defense_invalid_flight_direction():
    # Act and # Assert
    with pytest.raises(InvalidParameter):
        battle_service.add_plane_to_battle_defense_by_challenger(6, 1, 3, 5, 10)
