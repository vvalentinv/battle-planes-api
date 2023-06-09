from unittest import mock
from unittest.mock import Mock

import pytest
from controller.battle import battle_service
from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from model.battle import Battle
from model.plane import Plane
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
    assert str(e.value) == 'Not a positive int'


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


def test_start_battle_valid_user_id_concluded_battle(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return False

    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 0, 2,
                      [1, 2, 3], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    def mock_is_concluded(self, battle_id):
        return True

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    mocker.patch('dao.battle.BattleDao.is_concluded', mock_is_concluded)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.start_battle_by_challenger(1, 12)
    assert str(e.value) == 'This battle was concluded'


def test_start_battle_valid_user_id_valid_battle(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return False

    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 0, 2,
                      [1, 2, 3], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    def mock_is_concluded(self, battle_id):
        return False

    def mock_is_time_left(self, battle_id):
        return True

    def mock_add_challenger_to_battle(self, user_id, battle_id, defense_size):
        return 'Challenge accepted!'

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    mocker.patch('dao.battle.BattleDao.is_concluded', mock_is_concluded)
    mocker.patch('dao.battle.BattleDao.is_time_left', mock_is_time_left)
    mocker.patch('dao.battle.BattleDao.add_challenger_to_battle', mock_add_challenger_to_battle)
    # Act
    actual = battle_service.start_battle_by_challenger(1, 12)
    expected = 'Challenge accepted!'
    # Assert
    assert actual == expected


def test_start_battle_valid_user_id_valid_battle_time_elapsed(mocker):
    # Arrange
    def mock_is_engaged(self, user_id):
        return False

    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 0, 2,
                      [1, 2, 3], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    def mock_is_concluded(self, battle_id):
        return False

    def mock_is_time_left(self, battle_id):
        return False

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    mocker.patch('dao.battle.BattleDao.is_concluded', mock_is_concluded)
    mocker.patch('dao.battle.BattleDao.is_time_left', mock_is_time_left)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.start_battle_by_challenger(1, 12)
    assert str(e.value) == 'Timeframe for challenge just elapsed'


def test_add_plane_to_battle_defense_by_challenger_valid_ints():
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(1, 2, 3, 4, 30)
    assert str(e.value) == 'Battlefield size is between 10 and 15 inclusive.'


def test_add_plane_to_battle_defense_by_challenger_invalid_battle_id(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 1, 2,
                      [1, 2, 3], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(12, 1, 3, 4, 10)
    assert str(e.value) == 'Request rejected2'


def test_add_plane_to_battle_defense_by_challenger_defense_size_at_max(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return None

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(1, 2, 3, 4, 10)
    assert str(e.value) == 'Request rejected1'


def test_add_plane_to_battle_defense_by_challenger_invalid_user_id(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 3, 2,
                      [1, 2], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(12, 1, 3, 4, 10)
    assert str(e.value) == 'Request rejected3'


def test_add_plane_to_battle_defense_by_challenger_invalid_plane_db(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 1, 2,
                      [1, 2], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    def mock_get_plane_id(self, cockpit, flight_direction, sky_size):
        return None

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    mocker.patch('dao.plane.PlaneDao.get_plane_id', mock_get_plane_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(12, 1, 2, 2, 10)
    assert str(e.value) == 'Invalid selection'


def test_add_plane_to_battle_defense_by_challenger_def_length_1(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 1, 2,
                      [125], [1, 2, 3], 10, None, None, None, None, None, 3, None)

    def mock_get_plane_id(self, cockpit, flight_direction, sky_size):
        return 125

    def mock_get_plane_by_plane_id(self, plane_id):
        if plane_id == 125:
            return Plane(125, 2, 1, [10, 11, 12, 13, 14, 22, 31, 32, 33], 10)
        else:
            return Plane(88, 7, 1, [15, 16, 17, 18, 19, 27, 36, 37, 38], 10)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    mocker.patch('dao.plane.PlaneDao.get_plane_id', mock_get_plane_id)
    mocker.patch('dao.plane.PlaneDao.get_plane_by_plane_id', mock_get_plane_by_plane_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(12, 1, 2, 1, 10)
    assert str(e.value) == 'Overlapping planes'


def test_add_plane_to_battle_defense_by_challenger_def_length_0(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 1, 2,
                      None, [1, 2, 3], 10, None, None, None, None, None, 3, None)

    def mock_get_plane_id(self, cockpit, flight_direction, sky_size):
        return 125

    def mock_get_plane_by_plane_id(self, plane_id):
        return Plane(125, 2, 1, [10, 11, 12, 13, 14, 22, 31, 32, 33], 10)

    def mock_is_time_left(self, battle_id):
        return False

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    mocker.patch('dao.plane.PlaneDao.get_plane_id', mock_get_plane_id)
    mocker.patch('dao.plane.PlaneDao.get_plane_by_plane_id', mock_get_plane_by_plane_id)
    mocker.patch('dao.battle.BattleDao.is_time_left', mock_is_time_left)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(12, 1, 2, 1, 10)
    assert str(e.value) == 'Time frame to add planes for defense setup elapsed.'


def test_add_plane_to_battle_defense_by_challenger_def_length_0_in_time(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 1, 2,
                      None, [1, 2, 3], 10, None, None, None, None, None, 3, None)

    def mock_get_plane_id(self, cockpit, flight_direction, sky_size):
        return 125

    def mock_get_plane_by_plane_id(self, plane_id):
        return Plane(125, 2, 1, [10, 11, 12, 13, 14, 22, 31, 32, 33], 10)

    def mock_is_time_left(self, battle_id):
        return True

    def mock_add_planes_to_battle_defense_by_username(self, battle_id, defense):
        return '2 more plane(s) to add until defense setup is complete.'

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    mocker.patch('dao.plane.PlaneDao.get_plane_id', mock_get_plane_id)
    mocker.patch('dao.plane.PlaneDao.get_plane_by_plane_id', mock_get_plane_by_plane_id)
    mocker.patch('dao.battle.BattleDao.is_time_left', mock_is_time_left)
    mocker.patch('dao.battle.BattleDao.add_planes_to_battle_defense_by_username',
                 mock_add_planes_to_battle_defense_by_username)
    # Act
    actual = battle_service.add_plane_to_battle_defense_by_challenger(12, 1, 2, 1, 10)
    expected = '2 more plane(s) to add until defense setup is complete.'
    # Assert
    assert actual == expected


def test_get_status_invalid_battle_id(mocker):
    # Arrange
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.get_status(1, -3)
    assert str(e.value) == 'Not a positive int'


def test_get_status_valid_battle_id_invalid_in_db(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return None

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.get_status(1, 12)
    assert str(e.value) == 'Request rejected'


def test_get_status_valid_battle_id_valid_in_db_concluded_battle(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 1, 2, [1, 2, 3], [1, 2, 3], 10, None, None, None, None, True, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.get_status(1, 12)
    assert str(e.value) == 'Use battle history'


def test_get_status_unfinished_def_setup(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1,
                      [1], [1, 2, 3], 10, None, None, None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(2, 12)
    expected = None, None, None
    # Assert
    assert actual == expected


def test_get_status_challenger_on_challenger_turn_in_time(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1,
                      [1, 2, 3], [1, 2, 3], 10, None, None, None, None, False, 3, True)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(2, 12)
    expected = [], [None, [1, 2, 3], None], 'This is your turn to attack.'
    # Assert
    assert actual == expected


def test_get_status_challenger_on_challenged_turn_false_progress_false_disconnect(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1,
                      [1, 2, 3], [1, 2, 3], 10, [77], None, None, None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(2, 12)
    expected = [(77, 'Miss')], [[77], [1, 2, 3], None], "Wait for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_challenger_on_challenged_turn_true_progress_false_disconnect(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1,
                      [1, 2, 3], [1, 2, 3], 10, [77, 78, 79], [63, 37], None, None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(2, 12)
    expected = [(77, 'Miss'), (78, 'Miss'), (79, 'Miss')], \
               [[77, 78, 79], [1, 2, 3], [63, 37]], "Wait for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_challenger_on_challenged_turn_true_progress_true_disconnect_self_progress_false(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [77, 78, 79, 80, 81],
                      [78, 79, 80, 81], None, [78, 79, 80, 81], False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(2, 12)
    expected = 'Battle inconclusive by opponent disconnect.'
    # Assert
    assert actual == expected


def test_get_status_challenger_on_challenged_turn_true_progress_true_disconnect_self_progress_true(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [77, 78, 79, 37, 63],
                      [78, 79, 80, 81], None, [78, 79, 80, 81], False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(2, 12)
    expected = [(77, 'Miss'), (78, 'Miss'), (79, 'Miss'), (37, 'Kill'), (63, 'Kill')], \
               [[77, 78, 79, 37, 63], [1, 2, 3], [78, 79, 80, 81]], "Wait for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_challenger_on_challenger_turn_false_not_in_time(mocker):
    # Arrange

    m = Mock()
    m.side_effect = [Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [77, 78, 79, 80],
                            [78, 79, 80, 81], None, None, False, 3, False),
                     Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [77, 78, 79, 80, 22],
                            [78, 79, 80, 81], None, None, False, 3, False)
                     ]

    def mock_get_battle_by_id(self, battle_id):
        return m()

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 22

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.get_status(2, 12)
        expected = [(77, 'Miss'), (78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (22, 'Hit')], \
                   [[77, 78, 79, 80, 22], [1, 2, 3], [78, 79, 80, 81]], "Failed to attack -> system attack. Wait" \
                                                                        " for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_challenged_on_challenger_turn_in_time(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1,
                      [1, 2, 3], [1, 2, 3], 10, [0], None, None, None, False, 3, True)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(1, 12)
    expected = [], [None, [1, 2, 3], [0]], 'This is your turn to attack.'
    # Assert
    assert actual == expected


def test_get_status_challenged_on_challenged_turn_false_progress_false_disconnect(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1,
                      [1, 2, 3], [1, 2, 3], 10, [77], [0], None, None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(1, 12)
    expected = [(0, 'Miss')], [[0], [1, 2, 3], [77]], "Wait for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_challenged_on_challenged_turn_true_progress_false_disconnect(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1,
                      [1, 2, 3], [1, 2, 3], 10, [77, 63, 37], [0, 9, 90], None, None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(1, 12)
    expected = [(0, 'Miss'), (9, 'Miss'), (90, 'Miss')], \
               [[0, 9, 90], [1, 2, 3], [77, 63, 37]], "Wait for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_challenged_on_challenged_turn_true_progress_true_disconnect_self_progress_false(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(1, 12)
    expected = 'Battle inconclusive by player disconnect.'
    # Assert
    assert actual == expected


def test_get_status_challenged_on_challenger_turn_true_progress_true_disconnect_self_progress_true(mocker):
    # Arrange
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 37, 63], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.get_status(1, 12)
    expected = [(78, 'Miss'), (79, 'Miss'), (37, 'Kill'), (63, 'Kill')], \
               [[78, 79, 37, 63], [1, 2, 3], [78, 79, 80, 81]], "Wait for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_challenged_on_challenged_turn_false_not_in_time(mocker):
    # Arrange

    m = Mock()
    m.side_effect = [Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [77, 78, 79, 80],
                            [78, 79, 80], None, None, False, 3, False),
                     Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [77, 78, 79, 80],
                            [78, 79, 80, 23], None, None, False, 3, False)
                     ]

    def mock_get_battle_by_id(self, battle_id):
        return m()

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 23

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.get_status(1, 12)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (23, 'Hit')], \
                   [[78, 79, 80, 23], [1, 2, 3], [77, 78, 79, 80]], "Failed to attack -> system attack. Wait" \
                                                                    " for your opponent's attack."
    # Assert
    assert actual == expected


def test_get_status_non_challenger_or_challenged_id(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.get_status(3, 12)
    assert str(e.value) == 'This battle is private.'


def test_battle_update_invalid_battle_id_in_db(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return None

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.battle_update(2, 12, 21)
    assert str(e.value) == 'Request rejected'


def test_battle_update_valid_battle_id_concluded_true(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, True, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.battle_update(2, 12, 21)
    assert str(e.value) == 'Request rejected'


def test_battle_update_valid_battle_id_invalid_attack(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.battle_update(2, 12, 100)
    assert str(e.value) == 'Invalid parameter(s).'


def test_battle_update_valid_battle_id_invalid_user_id(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.battle_update(3, 12, 99)
    assert str(e.value) == 'Request rejected'


def test_battle_update_challenger_already_used_attack(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.battle_update(2, 12, 81)
    assert str(e.value) == 'Attack already used'


def test_battle_update_challenged_already_used_attack(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.battle_update(1, 12, 80)
    assert str(e.value) == 'Attack already used'


def test_battle_update_challenger_battle_turn_false(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81, 82],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.battle_update(2, 12, 81)
    assert str(e.value) == 'Wait for your turn.'


def test_battle_update_challenged_battle_turn_false(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, None)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act and # Assert
    with pytest.raises(Forbidden) as e:
        battle_service.battle_update(1, 12, 81)
    assert str(e.value) == 'Wait for your turn.'


def test_battle_update_challenger_valid_turn_valid_attack_in_time_self_progres_false_not_won(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], None, None, False, 3, True)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.battle_update(2, 12, 82)
    expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (82, 'Miss')]
    # Assert
    assert actual == expected


def test_battle_update_challenged_valid_turn_valid_attack_in_time_self_progres_false_not_won(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81, 82],
                      [78, 79, 80, 81], None, None, False, 3, True)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)
    # Act
    actual = battle_service.battle_update(1, 12, 82)
    expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (82, 'Miss')]
    # Assert
    assert actual == expected


def test_battle_update_challenger_valid_turn_valid_attack_not_in_time_self_progres_false_not_won(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 23

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(2, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (23, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenged_valid_turn_valid_attack_not_in_time_self_progres_false_not_won(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81, 82],
                      [78, 79, 80, 81], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 24

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(1, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (24, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenger_valid_turn_valid_attack_not_in_time_self_progres_true_opponents_false(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 63, 37],
                      [78, 79, 80, 81], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 23

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(2, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (63, 'Kill'), (37, 'Kill'), (23, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenged_valid_turn_valid_attack_not_in_time_self_progres_true_opponents_false(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81, 82],
                      [78, 79, 63, 37], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 24

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(1, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (63, 'Kill'), (37, 'Kill'), (24, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenger_valid_turn_valid_attack_not_in_time_self_progres_false_opponents_true(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 63, 37], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 23

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(2, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (23, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenged_valid_turn_valid_attack_not_in_time_self_progres_false_opponents_true(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 63, 37, 82],
                      [78, 79, 80, 81], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 24

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(1, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (24, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenger_valid_turn_valid_attack_not_in_time_self_progres_false_disconnect_valid_opponents_progress_true(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 63, 37], [78, 79, 80, 81], None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 23

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(2, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (23, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenged_valid_turn_valid_attack_not_in_time_self_progres_false_disconnect_valid_opponents_progress_true(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 63, 37, 82],
                      [78, 79, 80, 81], None, [78, 79, 80, 81], False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 24

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(1, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (24, 'Hit')]
    # Assert
    assert actual == expected


def test_battle_update_challenger_valid_turn_valid_attack_not_in_time_self_progres_false_disconnect_valid_opponents_progress_false(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81],
                      [78, 79, 80, 81], [78, 79, 80, 81], None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 23

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(2, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (23, 'Hit'), 'Battle inconclusive by '
                                                                                         'player disconnect.']
    # Assert
    assert actual == expected


def test_battle_update_challenged_valid_turn_valid_attack_not_in_time_self_progres_false_disconnect_valid_opponents_progress_false(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 80, 81, 82],
                      [78, 79, 80, 81], None, [78, 79, 80, 81], False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 24

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(1, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (80, 'Miss'), (81, 'Miss'), (24, 'Hit'), 'Battle inconclusive by '
                                                                                         'player disconnect.']
    # Assert
    assert actual == expected


def test_battle_update_challenger_valid_turn_valid_attack_not_in_time_self_progres_true_won(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 63, 37],
                      [78, 79, 80, 81], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 25

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(2, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (63, 'Kill'), (37, 'Kill'), (25, 'Kill'), 'Battle won by last attack!']
    # Assert
    assert actual == expected


def test_battle_update_challenged_valid_turn_valid_attack_not_in_time_self_progres_true_won(mocker):
    def mock_get_battle_by_id(self, battle_id):
        return Battle(12, 2, 1, [1, 2, 3], [1, 2, 3], 10, [78, 79, 63, 37, 82],
                      [78, 79, 63, 37], None, None, False, 3, False)

    mocker.patch('dao.battle.BattleDao.get_battle_by_id', mock_get_battle_by_id)

    # Act
    def mocked_random_choice(x, y):
        return 25

    with mock.patch('random.randint', mocked_random_choice):
        actual = battle_service.battle_update(1, 12, 82)
        expected = [(78, 'Miss'), (79, 'Miss'), (63, 'Kill'), (37, 'Kill'), (25, 'Kill'), 'Battle won by last attack!']
    # Assert
    assert actual == expected


def test_get_unchallenged_battles_not_engaged(mocker):
    def mock_get_unchallenged_battles(self, battle_id):
        return [Battle(99, 0, 1, None, [1, 2, 3], 10, None, None, None, None, False, 3, True),
                Battle(100, 0, 2, None, [1, 2, 3], 10, None, None, None, None, False, 3, True)]

    def mock_is_engaged(self, user_id):
        return False

    m = Mock()
    m.side_effect = [User(1, 'jcad1', '$2b$12$kcvn4uWQAKdu.ZJ1Mv4KV./XBKlIrjTiNkcARUxBZMdCuUC.JixoG', 'a@a.ca'),
                     User(2, 'jcad2', '$2b$12$kcvn4uWQAKdu.ZJ1Mv4KV./XBKlIrjTiNkcARUxBZMdCuUC.JixoG', 'a2@a.ca')]

    def mock_get_user_by_id(self, battle_id):
        return m()
    mocker.patch('dao.battle.BattleDao.get_unchallenged_battles', mock_get_unchallenged_battles)
    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)
    mocker.patch('dao.user.UserDao.get_user_by_id', mock_get_user_by_id)

    # Act

    actual = battle_service.get_unchallenged_battles(1)
    expected = [['jcad1', 3, 10], ['jcad2', 3, 10]]
    # Assert
    assert actual == expected


def test_get_unchallenged_battles_engaged(mocker):
    def mock_is_engaged(self, user_id):
        return True

    mocker.patch('dao.battle.BattleDao.is_engaged', mock_is_engaged)

    actual = battle_service.get_unchallenged_battles(1)
    expected = ["Finish your current battle engagement, before attempting a new one!"]
    # Assert
    assert actual == expected


# input_validation_helper tests
def test_add_battle_invalid_int():
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_battle(1, [1, 2, 3], '2s', 10, 10)
    assert str(e.value) == 'Not a positive int'


def test_add_plane_to_battle_defense_invalid_flight_direction():
    # Act and # Assert
    with pytest.raises(InvalidParameter) as e:
        battle_service.add_plane_to_battle_defense_by_challenger(6, 1, 3, 5, 10)
    assert str(e.value) == 'Expected one of 1, 2, 3, or 4'
