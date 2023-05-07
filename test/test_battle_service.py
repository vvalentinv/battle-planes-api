import pytest

from controller.battle import battle_service
from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from model.battle import Battle
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


def test_add_battle_invalid_user_id_in_db(mocker):
    # Arrange
    def mock_get_user_by_id(self, user_id):
        return False

    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.add_battle(1, [1, 2, 3], 3, 10, 10)
    assert str(e.value) == 'Request rejected!'


def test_add_battle_valid_user_id_user_already_in_active_battle(mocker):
    # Arrange
    def mock_get_user_by_id(self, user_id):
        return User(1, 'jcad1', 'some_password_hash', 'some_email')

    def mock_is_engaged(self, user_id):
        return True

    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)
    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.add_battle(1, [1, 2, 3], 3, 10, 10)
    assert str(e.value) == 'You are already engaged in another battle'


def test_start_battle_valid_user_id_user_already_in_active_battle(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return True

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.start_battle_by_challenger(2, 12)
    assert str(e.value) == 'You are already engaged in another battle'


def test_start_battle_valid_user_id_user_invalid_battle_id(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return False

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.start_battle_by_challenger(2, 'a12')
    assert str(e.value) == 'Expected digits only in a number'


def test_start_battle_valid_user_id_user_invalid_battle_id_in_db(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return False

    def mock_get_battle_by_id(self, battle_id):
        return None

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.start_battle_by_challenger(2, 12)
    assert str(e.value) == 'Request rejected'


def test_start_battle_valid_user_id_battle_already_challenged(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return False

    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 8, 2,
                      [1, 2, 3], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.start_battle_by_challenger(2, 12)
    assert str(e.value) == 'This player was already challenged.'


def test_start_battle_valid_user_id_battle_challenger_same_as_challenged(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return False

    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 0, 2,
                      [1, 2, 3], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.start_battle_by_challenger(2, 12)
    assert str(e.value) == 'Players cannot challenge themselves'


# input_validation_helper tests
def test_add_battle_invalid_int():
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_battle(1, [1, 2, 3], '2s', 10, 10)
    assert str(e.value) == 'Expected digits only in a number'


def test_add_plane_to_battle_defense_invalid_flight_direction():
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(6, 1, 3, 5, 10)
    assert str(e.value) == 'Expected one of 1, 2, 3, or 4'
