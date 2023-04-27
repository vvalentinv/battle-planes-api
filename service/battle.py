from dao.battle import BattleDao
from dao.plane import PlaneDao
from dao.user import UserDao
from exception.busy_player import BusyPlayer
from model.battle import Battle
from utilities.helper import validate_int
from exception.invalid_parameter import InvalidParameter


class BattleService:
    def __init__(self):
        self.battle_dao = BattleDao()
        self.plane_dao = PlaneDao()
        self.user_dao = UserDao()

    def add_plane_to_battle_defense_by_username(self, battle_id, username, cockpit, flight_direction, sky_size):
        if validate_int(battle_id) and validate_int(cockpit) and validate_int(flight_direction) \
                and validate_int(sky_size) and 9 < sky_size < 16:
            b = self.battle_dao.get_battle_by_id(battle_id)
            user = self.user_dao.get_user_by_username(username)
            if b.get_challenger_id() == user.get_user_id():
                plane_id = self.plane_dao.get_plane_id(cockpit, flight_direction, sky_size)
                plane_ids = None
                if plane_id is not None:
                    plane_ids = b.get_challenger_defense()
                    plane_ids.append(plane_id)
                return self.battle_dao.add_plane_to_battle_defense_by_username(battle_id, plane_ids, username)
        else:
            raise InvalidParameter("Battlefield size is between 10 and 15 inclusive.")

    def start_battle_by_challenger(self, username, battle_id):
        # add check for challenger engaged in active battle
        if validate_int(battle_id):
            pass
        battle = self.battle_dao.get_battle_by_id(battle_id)
        if battle is None:
            raise InvalidParameter("Request rejected")
        if battle and battle.get_challenger_id() > 0:
            raise BusyPlayer(f"{self.user_dao.get_user_by_username(battle.get_challenged_id())} "
                             f"has already engaged in battle!")
        elif battle.get_challenged_id() is not self.user_dao.get_user_by_username(username).get_user_id():
            raise InvalidParameter("Players cannot challenge themselves")
        return self.battle_dao.add_challenger_to_battle(self.user_dao.get_user_by_username(username), battle_id,
                                                        battle.get_defense_size())

    def add_battle(self, username, defense, defense_size, sky_size):
        # Check values
        # Check if user is already engaged in battle
        battle = Battle(None, None, self.user_dao.get_user_by_username(username).get_user_id(),
                        None, defense, sky_size, None, None, None, None, defense_size, None)
        return self.battle_dao.add_battle(battle)



