from dao.battle import BattleDao
from dao.plane import PlaneDao
from dao.user import UserDao
from exception.busy_player import BusyPlayer
from exception.forbidden import Forbidden
from model.battle import Battle
from utilities.helper import validate_int, validate_array_of_ints
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
                if plane_id is not None:
                    plane_ids = set()
                    if b.get_challenger_defense() is not None:
                        plane_ids.update(b.get_challenger_defense())
                    old_def_size = len(plane_ids)
                    plane_ids.add(plane_id)
                    if len(plane_ids) > old_def_size:
                        if b.get_defense_size() - len(plane_ids) >= 0 \
                                and self.battle_dao.is_time_left(b.get_battle_id()):
                            return self.battle_dao.add_plane_to_battle_defense_by_username(battle_id, list(plane_ids))
                        elif not self.battle_dao.is_time_left(b.get_battle_id()):
                            return "Time frame to add planes for defense setup elapsed."
                        else:
                            return "Maximum defense size reached."
                    else:
                        return "Invalid selection"

                else:
                    return "Invalid plane selection."
        else:
            raise InvalidParameter("Battlefield size is between 10 and 15 inclusive.")

    def start_battle_by_challenger(self, user_id, battle_id):
        if self.battle_dao.is_engaged(user_id):
            raise BusyPlayer("You are already engaged in another battle")
        if validate_int(battle_id):
            pass
        battle = self.battle_dao.get_battle_by_id(battle_id)
        if battle is None:
            raise InvalidParameter("Request rejected")
        elif battle.get_challenger_id() > 0:
            raise BusyPlayer("This player was already challenged.")
        elif battle.get_challenged_id() == user_id:
            raise InvalidParameter("Players cannot challenge themselves")
        elif self.battle_dao.is_concluded(battle_id):
            return "This battle was concluded"
        elif battle.get_challenger_id() == 0 and not self.battle_dao.is_time_left(battle_id):
            return self.battle_dao.add_challenger_to_battle(user_id, battle_id, battle.get_defense_size())
        return "Timeframe for challenge just elapsed"

    def add_battle(self, username, defense, defense_size, sky_size, max_time):
        if validate_int(defense_size) and validate_int(sky_size) \
                and validate_array_of_ints(defense) and validate_int(max_time):
            pass
        if self.battle_dao.is_engaged(self.user_dao.get_user_by_username(username).get_user_id()):
            raise Forbidden("You are already engaged in another battle")
        battle = Battle(None, None, self.user_dao.get_user_by_username(username).get_user_id(),
                        None, defense, sky_size, None, None, None, None, defense_size, None)
        return self.battle_dao.add_battle(battle, max_time)

    def get_status(self, user_id, battle_id):
        if validate_int(battle_id):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        if b.get_challenger_attacks() is None:
            chr_attacks = 0
        else:
            chr_attacks = len(b.get_challenger_attacks())
        if b.get_challenged_attacks() is None:
            chd_attacks = 0
        else:
            chd_attacks = len(b.get_challenger_attacks())

        if user_id == b.get_challenger_id():
            if chr_attacks == chd_attacks:
                return "This is your turn to attack."
            else:
                return "Wait for your opponent's attack."
        elif user_id == b.get_challenged_id():
            if chr_attacks > chd_attacks:
                return "This is your turn to attack."
            else:
                return "Wait for your opponent's attack."
        else:
            raise Forbidden("This battle is private.")
