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

    def start_battle_by_challenger(self, username, battle_id):
        battle_ready = self.battle_dao.get_battle_by_id(battle_id)
        if battle_ready is None:
            raise InvalidParameter("Request rejected")
        if battle_ready and battle_ready.get_challenger_id() > 0:
            raise BusyPlayer(f"{battle_ready.get_challenged_id()} has already engaged in battle!")
        return self.battle_dao.add_challenger_to_battle(self.user_dao.get_user_by_username(username), battle_id,
                                                        battle_ready.get_defense_size())



