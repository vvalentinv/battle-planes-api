from dao.battle import BattleDao
from dao.plane import PlaneDao
from dao.user import UserDao
from exception.forbidden import Forbidden
from model.battle import Battle
from utilities.input_validation_helper import validate_int, validate_array_of_ints
from utilities.helper import random_automatic_attack, evaluate_attack, evaluate_disconnect, check_progress
from exception.invalid_parameter import InvalidParameter


class BattleService:
    def __init__(self):
        self.battle_dao = BattleDao()
        self.plane_dao = PlaneDao()
        self.user_dao = UserDao()

    def add_plane_to_battle_defense_by_challenger(self, battle_id, user_id, cockpit, flight_direction, sky_size):
        if validate_int(battle_id) and validate_int(cockpit) and validate_int(flight_direction) \
                and validate_int(sky_size) and 9 < sky_size < 16:
            b = self.battle_dao.get_battle_by_id(battle_id)
            if b.get_challenger_id() == user_id and not b.get_concluded():
                plane_id = self.plane_dao.get_plane_id(cockpit, flight_direction, sky_size)
                if plane_id is not None:
                    plane_ids = set()
                    if b.get_challenger_defense() is not None:
                        plane_ids = set(b.get_challenger_defense())
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
            raise InvalidParameter("Battlefield size is between 10 and 15 inclusive.")

    def start_battle_by_challenger(self, user_id, battle_id):
        if self.battle_dao.is_engaged(user_id):
            raise Forbidden("You are already engaged in another battle")
        if validate_int(battle_id):
            pass
        battle = self.battle_dao.get_battle_by_id(battle_id)
        if battle is None:
            raise InvalidParameter("Request rejected")
        elif battle.get_challenger_id() > 0:
            raise Forbidden("This player was already challenged.")
        elif battle.get_challenged_id() == user_id:
            raise InvalidParameter("Players cannot challenge themselves")
        elif self.battle_dao.is_concluded(battle_id):
            return "This battle was concluded"
        elif battle.get_challenger_id() == 0 and self.battle_dao.is_time_left(battle_id):
            return self.battle_dao.add_challenger_to_battle(user_id, battle_id, battle.get_defense_size())
        return "Timeframe for challenge just elapsed"

    def add_battle(self, user_id, defense, defense_size, sky_size, max_time):
        if validate_int(defense_size) and validate_int(sky_size) \
                and validate_array_of_ints(defense) and validate_int(max_time):
            self.battle_dao.conclude_unchallenged_battles(user_id)
        if self.battle_dao.is_engaged(user_id):
            raise Forbidden("You are already engaged in another battle")
        battle = Battle(None, None, user_id,
                        None, defense, sky_size, None, None, None, None, None, defense_size, None)
        return self.battle_dao.add_battle(battle, max_time)

    def get_status(self, user_id, battle_id):
        messages = None
        data = None
        turn = None
        if validate_int(battle_id):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        if b is None:
            raise Forbidden("Request rejected")
        if b.get_concluded():
            raise InvalidParameter("Use battle history")
        cr_attacks = b.get_challenger_attacks() or []
        cd_attacks = b.get_challenged_attacks() or []
        cr_defense = b.get_challenger_defense() or []
        cd_defense = b.get_challenged_defense() or []
        cr_rnd_attacks = b.get_rnd_attack_er() or []
        cd_rnd_attacks = b.get_rnd_attack_ed() or []
        # conclude unfinished defense setups
        if b.get_challenger_id() and not len(cr_defense) == len(cd_defense) \
                and not self.battle_dao.is_time_left(battle_id):
            self.battle_dao.conclude_unfinished_battle(battle_id)
        elif user_id == b.get_challenger_id():
            data = [b.get_challenger_attacks(), b.get_challenger_defense(), b.get_challenged_attacks()]
            planes = []
            for plane_id in b.get_challenged_defense():
                planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
            messages = evaluate_attack(cr_attacks, planes)
            if len(cr_attacks) == len(cd_attacks) and self.battle_dao.is_time_left(battle_id):
                turn = "This is your turn to attack."
            elif len(cr_attacks) == len(cd_attacks) + 1 and self.battle_dao.is_time_left(battle_id):
                turn = "Wait for your opponent's attack."
                check_opponent_overall_progress = check_progress(cd_attacks, planes, b.get_defense_size())
                if evaluate_disconnect(cd_attacks, cd_rnd_attacks, check_opponent_overall_progress):
                    self.battle_dao.conclude_unfinished_battle(battle_id)
                    return "Battle inconclusive by player disconnect."
            # perform auto attack if turn expired
            elif len(cr_attacks) == len(cd_attacks) and not self.battle_dao.is_time_left(battle_id):
                attack = random_automatic_attack(cr_attacks, b.get_sky_size())
                cr_rnd_attacks.append(attack)
                cr_attacks.append(attack)
                self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks)
                self.battle_dao.add_random_challenger_attacks_to_battle(battle_id, cr_rnd_attacks)
                turn = "Failed to attack -> system attack. Wait for your opponent's attack."
        elif user_id == b.get_challenged_id():
            data = [b.get_challenged_attacks(), b.get_challenged_defense(), b.get_challenger_attacks()]
            planes = []
            for plane_id in b.get_challenger_defense():
                planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
            messages = evaluate_attack(cd_attacks, planes)
            if len(cr_attacks) == len(cd_attacks) + 1 and self.battle_dao.is_time_left(battle_id):
                turn = "This is your turn to attack."
            elif len(cr_attacks) == len(cd_attacks) and self.battle_dao.is_time_left(battle_id):
                turn = "Wait for your opponent's attack."
                check_opponent_overall_progress = check_progress(cr_attacks, planes, b.get_defense_size())
                if evaluate_disconnect(cr_attacks, cr_rnd_attacks, check_opponent_overall_progress):
                    self.battle_dao.conclude_unfinished_battle(battle_id)
                    return "Battle inconclusive by player disconnect."
            # perform auto attack if turn expired
            elif len(cr_attacks) == len(cd_attacks) + 1 and not self.battle_dao.is_time_left(battle_id):
                attack = random_automatic_attack(cd_attacks, b.get_sky_size())
                cd_rnd_attacks.append(attack)
                cd_attacks.append(attack)
                self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks)
                self.battle_dao.add_random_challenged_attacks_to_battle(battle_id, cd_rnd_attacks)
                turn = "Failed to attack -> system attack. Wait for your opponent's attack."
        else:
            raise Forbidden("This battle is private.")
        return messages, data, turn

    def battle_update(self, user_id, battle_id, attack):
        if validate_int(battle_id) and validate_int(attack):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        if b is None or b.get_concluded():
            raise Forbidden("Request rejected")
        not_rand = self.battle_dao.is_time_left(battle_id)
        sky = b.get_sky_size()
        if attack not in range(sky * sky):
            raise InvalidParameter("Invalid parameter(s).")
        cr = b.get_challenger_id()
        cd = b.get_challenged_id()
        cr_attacks = b.get_challenger_attacks() or []
        cd_attacks = b.get_challenged_attacks() or []
        cr_rnd_attacks = b.get_rnd_attack_er() or []
        cd_rnd_attacks = b.get_rnd_attack_ed() or []
        cr_defense = b.get_challenger_defense()
        cd_defense = b.get_challenged_defense()
        def_size = b.get_defense_size()
        cr_planes = []
        for plane_id in cd_defense:
            cr_planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
        cd_planes = []
        for plane_id in cr_defense:
            cd_planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
        if not cr == user_id and not cd == user_id and cr == 0:
            raise Forbidden("Request rejected. not playing")
        check_opponents_overall_progress = False
        # Perform attack, evaluate params and determine attack, store attack
        if cr == user_id:
            # check if it's challenger's turn (attack fields have same lengths
            if attack in cr_attacks:
                raise InvalidParameter("Attack already used")
            # challenged player's turn
            elif len(cr_attacks) > len(cd_attacks):
                raise InvalidParameter("Wait for your turn.")
            elif len(cr_attacks) == len(cd_attacks) and attack not in cr_attacks:
                if not not_rand:
                    attack = random_automatic_attack(cr_attacks, b.get_sky_size())
                    cr_rnd_attacks.append(attack)
                cr_attacks.append(attack)
            if not_rand:
                self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks)
            else:
                self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks)
                self.battle_dao.add_random_challenger_attacks_to_battle(battle_id, cr_rnd_attacks)
            # Next var determines if a battle is finished playing against random attacks or inconclusive by
            # disconnection
            check_opponent_overall_progress = check_progress(cd_attacks, cr_planes, def_size)
            if evaluate_disconnect(cr_attacks, cr_rnd_attacks, check_opponent_overall_progress):
                self.battle_dao.conclude_unfinished_battle(battle_id)
                return "Battle inconclusive by player disconnect."
            messages = evaluate_attack(cr_attacks, cd_planes)
            if messages[-1] == "Battle won by last attack!":
                self.battle_dao.conclude_won_battle(battle_id)
            return messages
        else:
            if attack in cd_attacks:
                raise InvalidParameter("Attack already used")
            elif len(cr_attacks) == len(cd_attacks):
                raise InvalidParameter("Wait for your turn.")
            elif len(cr_attacks) > len(cd_attacks) and attack not in cd_attacks:
                if not not_rand:
                    attack = random_automatic_attack(cd_attacks, b.get_sky_size())
                    cd_rnd_attacks.append(attack)
                cd_attacks.append(attack)
            if not_rand:
                self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks)
            else:
                self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks)
                self.battle_dao.add_random_challenged_attacks_to_battle(battle_id, cd_rnd_attacks)
            # Next var determines if a battle is finished playing against random attacks or inconclusive by
            # disconnection
            check_opponent_overall_progress = check_progress(cr_attacks, cd_planes, def_size)
            if evaluate_disconnect(cd_attacks, cd_rnd_attacks, check_opponent_overall_progress):
                self.battle_dao.conclude_unfinished_battle(battle_id)
                return "Battle inconclusive by player disconnect."
            messages = evaluate_attack(cd_attacks, cr_planes)
            if messages[-1] == "Battle won by last attack!":
                self.battle_dao.conclude_won_battle(battle_id)
            return messages
