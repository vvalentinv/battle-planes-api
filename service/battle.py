from dao.battle import BattleDao
from dao.plane import PlaneDao
from dao.user import UserDao
from exception.busy_player import BusyPlayer
from utilities.helper import validate_int, validate_flight_direction, validate_username
from exception.invalid_parameter import InvalidParameter


class BattleService:
    def __init__(self):
        self.battle_dao = BattleDao()
        self.plane_dao = PlaneDao()
        self.user_dao = UserDao()

    def add_plane_to_battle_defense_by_username(self, battle_id, username, cockpit, flight_direction, sky_size):
        # TO DO check if logged-in user is one of battle users
        # TO DO bring username as param
        if validate_int(battle_id) and validate_int(cockpit) and validate_flight_direction(flight_direction) \
                and validate_int(sky_size) and 9 < sky_size < 16:
            plane_id = self.plane_dao.get_plane_id(cockpit, flight_direction, sky_size)
            plane_ids = None
            if plane_id is not None:
                position = self.battle_dao.get_defense_position(battle_id, username)
                plane_ids = list(self.battle_dao.get_defense_by_id_username_and_position(battle_id, username, position))
                plane_ids.append(plane_id)
            return self.battle_dao.add_plane_to_battle_defense_by_username(battle_id, plane_ids, username)
        else:
            raise InvalidParameter("Battlefield size is between 10 and 15 inclusive.")

    def add_new_battle(self, username, opponent):
        opponent_user = None
        if validate_username(opponent):
            opponent_user = self.user_dao.get_user_by_username(opponent)
        elif self.battle_dao.check_if_user_is_battle_ready:
            raise BusyPlayer(f"{opponent} has already engaged in battle!")
        return self.battle_dao.add_battle(self.user_dao.get_user_by_username(username), opponent_user)



