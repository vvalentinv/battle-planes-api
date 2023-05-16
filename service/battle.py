from dao.battle import BattleDao
from dao.plane import PlaneDao
from dao.user import UserDao
from exception.forbidden import Forbidden
from model.battle import Battle
from service.input_validation_helper import validate_int, validate_flight_direction, validate_array_of_ints
from utilities.helper import random_automatic_attack, evaluate_attack, evaluate_disconnect, check_progress, \
    validate_defense
from exception.invalid_parameter import InvalidParameter


class BattleService:
    def __init__(self):
        self.battle_dao = BattleDao()
        self.plane_dao = PlaneDao()
        self.user_dao = UserDao()

    def add_plane_to_battle_defense_by_challenger(self, battle_id, user_id, cockpit, flight_direction, sky_size):
        if validate_int(battle_id) and validate_int(cockpit) and validate_flight_direction(flight_direction) \
                and validate_int(sky_size) and 9 < sky_size < 16:
            b = self.battle_dao.get_battle_by_id(battle_id)
            if b is None:
                raise InvalidParameter("Request rejected1")
            existing_defense = b.get_challenger_defense() or []
            if b.get_defense_size() <= len(existing_defense):
                raise InvalidParameter("Request rejected2")
            elif not user_id == b.get_challenger_id():
                raise Forbidden("Request rejected3")
            plane_id = self.plane_dao.get_plane_id(cockpit, flight_direction, sky_size)
            if not plane_id:
                raise InvalidParameter("Invalid selection")
            planes = []
            if len(existing_defense) > 0:
                for p_id in existing_defense:
                    planes.append(self.plane_dao.get_plane_by_plane_id(p_id))
            if not validate_defense(self.plane_dao.get_plane_by_plane_id(plane_id), planes):
                raise Forbidden("Overlapping planes")
            if not self.battle_dao.is_time_left(b.get_battle_id()):
                raise Forbidden("Time frame to add planes for defense setup elapsed.")
            existing_defense.append(plane_id)
            return self.battle_dao.add_planes_to_battle_defense_by_username(battle_id, existing_defense)
        else:
            raise InvalidParameter("Battlefield size is between 10 and 15 inclusive.")

    def start_battle_by_challenger(self, user_id, battle_id):
        if self.battle_dao.is_engaged(user_id):
            raise Forbidden("You are already engaged in another battle")
        if validate_int(battle_id):
            battle = self.battle_dao.get_battle_by_id(battle_id)
            if battle is None:
                raise InvalidParameter("Request rejected")
            elif battle.get_challenger_id() > 0:
                raise Forbidden("This player was already challenged.")
            elif battle.get_challenged_id() == user_id:
                raise Forbidden("Players cannot challenge themselves")
            elif self.battle_dao.is_concluded(battle_id):
                raise InvalidParameter("This battle was concluded")
            elif battle.get_challenger_id() == 0 and self.battle_dao.is_time_left(battle_id):
                return self.battle_dao.add_challenger_to_battle(user_id, battle_id, battle.get_defense_size())
            raise InvalidParameter("Timeframe for challenge just elapsed")

    def add_battle(self, user_id, defense, defense_size, sky_size, max_time):
        if validate_int(defense_size) and validate_int(sky_size) \
                and validate_array_of_ints(defense) and validate_int(max_time):
            self.battle_dao.conclude_unchallenged_battles(user_id)
            if not self.user_dao.get_user_by_id(user_id):
                raise Forbidden("Request rejected!")
            elif self.battle_dao.is_engaged(user_id):
                raise Forbidden("You are already engaged in another battle")
            battle = Battle(None, None, user_id,
                            None, defense, sky_size, None, None, None, None, False, defense_size, None)
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
        # conclude challenged unfinished defense setups
        if not b.get_challenger_id() == 0 and not len(cr_defense) == len(cd_defense) \
                and not b.get_battle_turn():
            self.battle_dao.conclude_unfinished_battle(battle_id)
        elif user_id == b.get_challenger_id() and len(cr_defense) == len(cd_defense):
            data = [b.get_challenger_attacks(), b.get_challenger_defense(), b.get_challenged_attacks()]
            planes = []
            for plane_id in b.get_challenged_defense():
                planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
            my_planes = []
            for plane_id in b.get_challenger_defense():
                my_planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
            messages = evaluate_attack(cr_attacks, planes)
            if len(cr_attacks) == len(cd_attacks) and b.get_battle_turn():
                turn = "This is your turn to attack."
            elif len(cr_attacks) - 1 == len(cd_attacks):
                turn = "Wait for your opponent's attack."
                check_opponent_overall_progress = check_progress(cd_attacks, planes, b.get_defense_size())
                if evaluate_disconnect(cd_attacks, cd_rnd_attacks, check_opponent_overall_progress) \
                        and not check_progress(cr_attacks, my_planes, b.get_defense_size()):
                    self.battle_dao.conclude_unfinished_battle(battle_id)
                    return "Battle inconclusive by opponent disconnect."
            # perform auto attack if turn expired
            elif len(cr_attacks) == len(cd_attacks) and not b.get_battle_turn():
                attack = random_automatic_attack(cr_attacks, b.get_sky_size())
                cr_rnd_attacks.append(attack)
                cr_attacks.append(attack)
                self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks)
                self.battle_dao.add_random_challenger_attacks_to_battle(battle_id, cr_rnd_attacks)
                turn = "Failed to attack -> system attack. Wait for your opponent's attack."
                battle = self.battle_dao.get_battle_by_id(battle_id)
                data = [battle.get_challenger_attacks(), battle.get_challenger_defense(),
                        battle.get_challenged_attacks()]
                planes = []
                for plane_id in battle.get_challenged_defense():
                    planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
                messages = evaluate_attack(cr_attacks, planes)
        elif user_id == b.get_challenged_id() and len(cr_defense) == len(cd_defense):
            data = [b.get_challenged_attacks(), b.get_challenged_defense(), b.get_challenger_attacks()]
            planes = []
            for plane_id in b.get_challenger_defense():
                planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
            my_planes = []
            for plane_id in b.get_challenged_defense():
                my_planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
            messages = evaluate_attack(cd_attacks, planes)
            if len(cr_attacks) == len(cd_attacks) + 1 and b.get_battle_turn():
                turn = "This is your turn to attack."
            elif len(cr_attacks) == len(cd_attacks):
                turn = "Wait for your opponent's attack."
                check_opponent_overall_progress = check_progress(cr_attacks, planes, b.get_defense_size())
                if evaluate_disconnect(cr_attacks, cr_rnd_attacks, check_opponent_overall_progress) \
                        and not check_progress(cd_attacks, my_planes, b.get_defense_size()):
                    self.battle_dao.conclude_unfinished_battle(battle_id)
                    return "Battle inconclusive by player disconnect."
            # perform auto attack if turn expired
            elif len(cr_attacks) == len(cd_attacks) + 1 and not b.get_battle_turn():
                attack = random_automatic_attack(cd_attacks, b.get_sky_size())
                cd_rnd_attacks.append(attack)
                cd_attacks.append(attack)
                self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks)
                self.battle_dao.add_random_challenged_attacks_to_battle(battle_id, cd_rnd_attacks)
                turn = "Failed to attack -> system attack. Wait for your opponent's attack."
                battle = self.battle_dao.get_battle_by_id(battle_id)
                data = [battle.get_challenged_attacks(), battle.get_challenged_defense(),
                        battle.get_challenger_attacks()]
                planes = []
                for plane_id in battle.get_challenger_defense():
                    planes.append(self.plane_dao.get_plane_by_plane_id(plane_id))
                messages = evaluate_attack(cd_attacks, planes)
        else:
            raise Forbidden("This battle is private.")
        return messages, data, turn

    def battle_update(self, user_id, battle_id, attack):
        if validate_int(battle_id) and validate_int(attack):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        if b is None or b.get_concluded():
            raise Forbidden("Request rejected")
        if attack not in range(b.get_sky_size() * b.get_sky_size()):
            raise InvalidParameter("Invalid parameter(s).")
        cr = b.get_challenger_id()
        cd = b.get_challenged_id()
        if not cr == user_id and not cd == user_id:
            raise Forbidden("Request rejected")
        messages = None
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
        # Perform attack, evaluate params and determine attack, store attack
        if cr == user_id:
            # check if it"s challenger"s turn (attack fields have same lengths
            if attack in cr_attacks and not len(cr_attacks) > len(cd_attacks):
                raise InvalidParameter("Attack already used")
            # challenged player"s turn
            elif len(cr_attacks) > len(cd_attacks):
                raise Forbidden("Wait for your turn.")
            elif len(cr_attacks) == len(cd_attacks) and attack not in cr_attacks:
                if not b.get_battle_turn():
                    attack = random_automatic_attack(cr_attacks, b.get_sky_size())
                    cr_rnd_attacks.append(attack)
                    self.battle_dao.add_random_challenger_attacks_to_battle(battle_id, cr_rnd_attacks)
                cr_attacks.append(attack)
                self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks)
                # Next var determines if a battle is finished playing against random attacks or inconclusive by
                # disconnection
                messages = evaluate_attack(cr_attacks, cd_planes)
                check_overall_progress = check_progress(cr_attacks, cd_planes, def_size)
                if evaluate_disconnect(cr_attacks, cr_rnd_attacks, check_overall_progress) \
                        and not check_progress(cd_attacks, cr_planes, def_size):
                    self.battle_dao.conclude_unfinished_battle(battle_id)
                    messages.append("Battle inconclusive by player disconnect.")
                if messages[-1] == "Battle won by last attack!":
                    self.battle_dao.conclude_won_battle(battle_id)
        else:
            if attack in cd_attacks and not len(cr_attacks) == len(cd_attacks):
                raise InvalidParameter("Attack already used")
            elif len(cr_attacks) == len(cd_attacks):
                raise Forbidden("Wait for your turn.")
            elif len(cr_attacks) > len(cd_attacks) and attack not in cd_attacks:
                if not b.get_battle_turn():
                    attack = random_automatic_attack(cd_attacks, b.get_sky_size())
                    cd_rnd_attacks.append(attack)
                    self.battle_dao.add_random_challenged_attacks_to_battle(battle_id, cd_rnd_attacks)
                cd_attacks.append(attack)
                self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks)
                # Next var determines if a battle is finished playing against random attacks or inconclusive by
                # disconnection
                messages = evaluate_attack(cd_attacks, cr_planes)
                check_overall_progress = check_progress(cd_attacks, cr_planes, def_size)
                if evaluate_disconnect(cd_attacks, cd_rnd_attacks, check_overall_progress) \
                        and not check_progress(cr_attacks, cd_planes, def_size):
                    self.battle_dao.conclude_unfinished_battle(battle_id)
                    messages.append("Battle inconclusive by player disconnect.")

                if messages[-1] == "Battle won by last attack!":
                    self.battle_dao.conclude_won_battle(battle_id)
        return messages

    def get_unchallenged_battles(self, user_id):
        if self.battle_dao.is_engaged(user_id):
            return ["Finish your current battle engagement, before attempting a new one!"]
        unchallenged_battles = self.battle_dao.get_unchallenged_battles(user_id)
        data = []
        for b in unchallenged_battles:
            username = self.user_dao.get_user_by_id(b.get_challenged_id()).get_username()
            defense = b.get_defense_size()
            sky = b.get_sky_size()
            data.append([username, defense, sky])
        return data
