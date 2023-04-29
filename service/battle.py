from dao.battle import BattleDao
from dao.plane import PlaneDao
from dao.user import UserDao
from exception.busy_player import BusyPlayer
from exception.forbidden import Forbidden
from model.battle import Battle
from utilities.helper import validate_int, validate_array_of_ints, check_attack_effect, random_automatic_attack
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
                elif b.get_concluded():
                    return "Invalid battle"
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

    def add_battle(self, user_id, defense, defense_size, sky_size, max_time):
        if validate_int(defense_size) and validate_int(sky_size) \
                and validate_array_of_ints(defense) and validate_int(max_time):
            pass
        if self.battle_dao.conclude_unchallenged_battles(user_id) and \
                self.battle_dao.is_engaged(user_id):
            raise Forbidden("You are already engaged in another battle")
        battle = Battle(None, None, user_id,
                        None, defense, sky_size, None, None, None, None, defense_size, None)
        return self.battle_dao.add_battle(battle, max_time)

    def get_status(self, user_id, battle_id):
        if validate_int(battle_id):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        if b is None:
            raise Forbidden("Request rejected")
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

    def battle_update(self, user_id, battle_id, attack, sky_size):
        if validate_int(battle_id) and validate_int(attack) and validate_int(sky_size):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        if b is None or b.get_concluded():
            raise Forbidden("Request rejected")
        sky = b.get_sky_size()
        if attack not in range(sky_size * sky_size) or not sky == sky_size:
            raise InvalidParameter("Invalid parameter(s).")
        cr = b.get_challenger_id()
        cd = b.get_challenged_id()
        cr_attacks = b.get_challenger_attacks() or [0]
        cd_attacks = b.get_challenged_attacks() or [0]
        cr_defense = b.get_challenger_defense()
        cd_defense = b.get_challenged_defense()
        message = None
        cd_atk = cr_atk = None
        rand = False
        if not cr == user_id and not cd == user_id and cr == 0:
            raise Forbidden("Request rejected. not playing")
        if cr == user_id:
            # check if it's challenger's turn (attack fields have same lengths
            if len(cr_attacks) == len(cd_attacks) and attack not in cr_attacks:
                if not self.battle_dao.is_time_left(battle_id):
                    attack = random_automatic_attack(cr_attacks, b.get_sky_size())
                    rand = True
                print(attack)
                print(rand)
                # add attack value to battle
                # check for effect on defense
                # return message
                planes = []
                for plane_id in cd_defense:
                    planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
                message = check_attack_effect(attack, planes)
                print(message)
            elif attack in cr_attacks:
                raise InvalidParameter("Attack already used")
            # challenged player's turn
            elif len(cr_attacks) > len(cd_attacks):
                raise InvalidParameter("Wait for your turn.")
            if not rand:
                cr_atk = self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks.append(attack))
            else:
                pass
                # add code to update battle record data with rand attacks and able to identify consecutive rand attacks

        else:
            # check if it's challenger's turn (attack fields have same lengths
            if len(cr_attacks) > len(cd_attacks) and attack not in cd_attacks:
                if not self.battle_dao.is_time_left(battle_id):
                    attack = random_automatic_attack(cd_attacks, b.get_sky_size())
                    rand = True
                # add attack value to battle
                # check for effect on defense
                # return message
                planes = []
                for plane_id in cr_defense:
                    planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
                message = check_attack_effect(attack, planes)
            elif attack in cd_attacks:
                raise InvalidParameter("Attack already used")
            # challenger's turn
            elif len(cr_attacks) == len(cd_attacks):
                raise InvalidParameter("Wait for your turn.")
            if not rand:
                cd_atk = self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks.append(attack))
        if cr_atk or cd_atk:
            return message
        else:
            # add code to update battle record data with rand attacks and able to identify consecutive rand attacks
            pass




