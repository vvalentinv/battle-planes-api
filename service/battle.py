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
            if not self.battle_dao.is_time_left(b.get_battle_id()):
                self.battle_dao.conclude_unfinished_defense_setup_battle(battle_id)
                raise Forbidden("Time frame to add planes for defense setup elapsed.")
            existing_defense = b.get_challenger_defense() or []
            print(existing_defense)
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
                return self.battle_dao.add_challenger_to_battle(user_id, battle_id)
            raise InvalidParameter("Timeframe for challenge just elapsed")

    def add_battle(self, user_id, defense, defense_size, sky_size, max_time, turn_time):
        if validate_int(defense_size) and validate_int(sky_size) \
                and validate_array_of_ints(defense) and validate_int(max_time) and validate_int(turn_time):
            if self.battle_dao.is_engaged(user_id):
                raise Forbidden("You are already engaged in another battle")
            if not int(defense_size) == len(defense):
                raise InvalidParameter("Defense size not matching # of selected planes!")
            # Validate defense
            validated_defense = []
            for p_id in defense:
                plane = self.plane_dao.get_plane_by_plane_id(p_id)
                if plane:
                    if validate_defense(plane, validated_defense):
                        validated_defense.append(plane)
            if not len(validated_defense) == len(defense):
                raise InvalidParameter("Defense contains overlapping planes!")
            self.battle_dao.conclude_unchallenged_battles(user_id)
            self.battle_dao.conclude_unstarted_battle()
            battle = Battle(None, None, user_id,
                            None, defense, sky_size, None, None, None, None, False, defense_size, None, turn_time)
            return self.battle_dao.add_battle(battle, max_time, turn_time)

    def get_status(self, user_id, battle_id):
        messages = {"defense_messages": [], "attack_messages": []}
        data = {"my_attacks": [], "my_defense": [], "opponent_attacks": []}
        turn = {"turn": ""}
        params = {"sky": None, "defense": None, "time": None}
        if validate_int(battle_id):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        if b is None:
            raise Forbidden("Request rejected")
        if b.get_concluded():
            raise InvalidParameter("Use battle history")
        params["sky"] = b.get_sky_size()
        params["defense"] = b.get_defense_size()
        params["time"] = b.get_end_battle_turn_at()
        cr = b.get_challenger_id()
        cd = b.get_challenged_id()
        cr_attacks = b.get_challenger_attacks() or []
        cd_attacks = b.get_challenged_attacks() or []
        cr_defense = b.get_challenger_defense() or []
        cd_defense = b.get_challenged_defense() or []
        cr_rnd_attacks = b.get_rnd_attack_er() or []
        cd_rnd_attacks = b.get_rnd_attack_ed() or []
        sky_size = b.get_sky_size()
        in_time = b.check_end_battle_turn_at()
        turn_size = str(b.get_battle_turn_size()) + ' MINUTE'
        # conclude challenged unfinished defense setups
        if (user_id == cr or user_id == cd) and not len(cr_defense) == len(cd_defense) \
                and not in_time:
            self.battle_dao.conclude_unfinished_defense_setup_battle(battle_id)
        elif user_id == cr:
            for p_id in cr_defense:
                p = []
                plane = self.plane_dao.get_plane_by_plane_id(p_id)
                p.append(plane.get_cockpit())
                body = plane.get_body()
                for bo in body[0]:
                    p.append(bo)
                data["my_defense"].append(p)
            planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cd_defense]
            my_planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cr_defense]
            data["opponent_attacks"] = cd_attacks
            data["my_attacks"] = cr_attacks
            if len(cr_attacks) == len(cd_attacks):
                if in_time:
                    turn["turn"] = "This is your turn to attack."
                else:
                    attack = random_automatic_attack(cr_attacks, sky_size)
                    cr_rnd_attacks.append(attack)
                    cr_attacks.append(attack)
                    self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks, turn_size)
                    self.battle_dao.add_random_challenger_attacks_to_battle(battle_id, cr_rnd_attacks, turn_size)
                    turn["turn"] = "Wait for your opponent's attack."
            elif len(cr_attacks) - 1 == len(cd_attacks):
                turn["turn"] = "Wait for your opponent's attack."
            messages["attack_messages"] = evaluate_attack(cr_attacks, planes)
            messages["defense_messages"] = evaluate_attack(cd_attacks, my_planes)
            if len(messages["attack_messages"]) > 2 and messages["attack_messages"][-1] == "Battle won by last " \
                                                                                           "attack!":
                self.battle_dao.conclude_won_battle(battle_id, cr)
            if len(messages["defense_messages"]) > 2 and messages["defense_messages"][-1] == "Battle won by last " \
                                                                                             "attack!":
                self.battle_dao.conclude_won_battle(battle_id, cd)
        elif user_id == cd:
            for p_id in cd_defense:
                p = []
                plane = self.plane_dao.get_plane_by_plane_id(p_id)
                p.append(plane.get_cockpit())
                body = plane.get_body()
                for bo in body[0]:
                    p.append(bo)
                data["my_defense"].append(p)
            planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cr_defense]
            my_planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cd_defense]
            data["opponent_attacks"] = cr_attacks
            data["my_attacks"] = cd_attacks
            if len(cr_attacks) - 1 == len(cd_attacks):
                if in_time:
                    turn["turn"] = "This is your turn to attack."
                else:
                    attack = random_automatic_attack(cd_attacks, sky_size)
                    cd_rnd_attacks.append(attack)
                    cd_attacks.append(attack)
                    self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks, turn_size)
                    self.battle_dao.add_random_challenged_attacks_to_battle(battle_id, cd_rnd_attacks, turn_size)
                    turn["turn"] = "Wait for your opponent's attack."
            elif len(cr_attacks) == len(cd_attacks):
                if in_time:
                    turn["turn"] = "Wait for your opponent's attack."
                if not in_time:
                    attack = random_automatic_attack(cr_attacks, b.get_sky_size())
                    cr_rnd_attacks.append(attack)
                    cr_attacks.append(attack)
                    self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks, turn_size)
                    self.battle_dao.add_random_challenger_attacks_to_battle(battle_id, cr_rnd_attacks, turn_size)
            messages["attack_messages"] = evaluate_attack(cd_attacks, planes)
            messages["defense_messages"] = evaluate_attack(cr_attacks, my_planes)
            if len(messages["attack_messages"]) > 2 and messages["attack_messages"][-1] == "Battle won by last " \
                                                                                           "attack!":
                self.battle_dao.conclude_won_battle(battle_id, cr)
            if len(messages["defense_messages"]) > 2 and messages["defense_messages"][-1] == "Battle won by last " \
                                                                                             "attack!":
                self.battle_dao.conclude_won_battle(battle_id, cd)
        else:
            return "Waiting for challenger's defense setup!", None, b.get_end_battle_turn_at(), params
        return messages, data, turn, params

    def battle_update(self, user_id, battle_id, attack):
        if validate_int(battle_id) and validate_int(attack):
            pass
        b = self.battle_dao.get_battle_by_id(battle_id)
        attack = int(attack)
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
        sky_size = b.get_sky_size()
        b.get_defense_size()
        cr_planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cr_defense]
        cd_planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cd_defense]
        turn_size = str(b.get_battle_turn_size()) + ' MINUTE'
        in_time = b.check_end_battle_turn_at()
        # Perform attack, evaluate params and determine attack, store attack
        if cr == user_id:
            # check if it"s challenger"s turn (attack fields have same lengths
            if attack in cr_attacks:  # and not len(cr_attacks) > len(cd_attacks):
                raise InvalidParameter("Attack already used")
            # challenged player's turn
            elif len(cr_attacks) > len(cd_attacks):
                raise Forbidden("Wait for your turn.")
            elif len(cr_attacks) == len(cd_attacks) and attack not in cr_attacks:
                if not in_time:
                    attack = random_automatic_attack(cr_attacks, sky_size)
                    cr_rnd_attacks.append(attack)
                    self.battle_dao.add_random_challenger_attacks_to_battle(battle_id, cr_rnd_attacks, turn_size)
                cr_attacks.append(attack)
                self.battle_dao.add_challenger_attacks_to_battle(battle_id, cr_attacks, turn_size)

                messages = evaluate_attack(cr_attacks, cd_planes)
                # Next var determines if a battle is finished playing against random attacks or inconclusive by
                # disconnection
                check_overall_progress = check_progress(cr_attacks, cd_planes, cr_rnd_attacks)
                if evaluate_disconnect(cr_attacks, cr_rnd_attacks, check_overall_progress) \
                        and not check_progress(cd_attacks, cr_planes, cd_rnd_attacks):
                    self.battle_dao.conclude_unfinished_battle(battle_id, cr)
                    messages.append("Battle inconclusive by player disconnect.")
                if len(messages) > 2 and messages[-1] == "Battle won by last attack!":
                    self.battle_dao.conclude_won_battle(battle_id, cr)
        else:
            if attack in cd_attacks and not len(cr_attacks) == len(cd_attacks):
                raise InvalidParameter("Attack already used")
            elif len(cr_attacks) == len(cd_attacks):
                raise Forbidden("Wait for your turn.")
            elif len(cr_attacks) > len(cd_attacks) and attack not in cd_attacks:
                if not in_time:
                    attack = random_automatic_attack(cd_attacks, sky_size)
                    cd_rnd_attacks.append(attack)
                    self.battle_dao.add_random_challenged_attacks_to_battle(battle_id, cd_rnd_attacks, turn_size)
                cd_attacks.append(attack)
                self.battle_dao.add_challenged_attacks_to_battle(battle_id, cd_attacks, turn_size)
                # Next var determines if a battle is finished playing against random attacks or inconclusive by
                # disconnection
                messages = evaluate_attack(cd_attacks, cr_planes)
                check_overall_progress = check_progress(cd_attacks, cr_planes, cd_rnd_attacks)
                if evaluate_disconnect(cd_attacks, cd_rnd_attacks, check_overall_progress) \
                        and not check_progress(cr_attacks, cd_planes, cr_rnd_attacks):
                    self.battle_dao.conclude_unfinished_battle(battle_id, cd)
                    messages.append("Battle inconclusive by player disconnect.")

                if len(messages) > 2 and messages[-1] == "Battle won by last attack!":
                    self.battle_dao.conclude_won_battle(battle_id, cd)
        return messages

    def get_unchallenged_battles(self, user_id):
        data = {'message': "", 'battles': []}
        if self.battle_dao.is_engaged(user_id):
            data['message'] = "Finish your current battle engagement, before attempting a new one!"
        unchallenged_battles = self.battle_dao.get_unchallenged_battles() or []
        data['battles'] = []
        battle = self.battle_dao.get_defense_setup_for_challenger(user_id)
        defense = []
        cr_def = []
        if battle and battle.get_challenger_defense():
            for p_id in battle.get_challenger_defense():
                p = []
                plane = self.plane_dao.get_plane_by_plane_id(p_id)
                p.append(plane.get_cockpit())
                body = plane.get_body()
                for b in body[0]:
                    p.append(b)
                defense.append(p)
        if battle:
            cr_def = battle.get_challenger_defense() or []
        if battle is not None and len(cr_def) < battle.get_defense_size() and \
                data['message'] == "Finish your current battle engagement, before attempting a new one!":
            data['battles'].append(
                [battle.get_battle_id(), defense,
                 battle.get_defense_size(), battle.get_sky_size(), battle.get_end_battle_turn_at()])
        elif data['message'] == '':
            for b in unchallenged_battles:
                b_id = b.get_battle_id()
                username = self.user_dao.get_user_by_id(b.get_challenged_id()).get_username()
                defense = b.get_defense_size()
                sky = b.get_sky_size()
                data['battles'].append([b_id, defense, username, sky, b.get_end_battle_turn_at()])
        else:
            data['message'] = "Please resume battle screen"
        return data

    def get_battle_result(self, user_id, battle_id):
        messages = {"defense_messages": [], "attack_messages": []}
        data = {"my_attacks": [], "my_defense": [], "opponent_attacks": []}
        params = {"sky": None, "defense": None, "time": None}
        opponent = None
        if validate_int(battle_id):
            pass
        battle_id = int(battle_id)
        b = self.battle_dao.get_battle_by_id(battle_id)
        if not b.get_concluded():
            return "Unfinished battle"
        params["sky"] = b.get_sky_size()
        params["defense"] = b.get_defense_size()
        params["time"] = b.get_end_battle_turn_at()
        cr = b.get_challenger_id()
        cd = b.get_challenged_id()
        cr_attacks = b.get_challenger_attacks() or []
        cd_attacks = b.get_challenged_attacks() or []
        cr_defense = b.get_challenger_defense() or []
        cd_defense = b.get_challenged_defense() or []
        if b and user_id == cr:
            for p_id in cr_defense:
                p = []
                plane = self.plane_dao.get_plane_by_plane_id(p_id)
                p.append(plane.get_cockpit())
                body = plane.get_body()
                for bo in body[0]:
                    p.append(bo)
                data["my_defense"].append(p)
            data["my_attacks"] = cr_attacks
            data["opponent_attacks"] = cd_attacks
            opponent = cd
            planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cd_defense]
            my_planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cr_defense]
            messages["attack_messages"] = evaluate_attack(cr_attacks, planes)
            messages["defense_messages"] = evaluate_attack(cd_attacks, my_planes)
        elif user_id == cd:
            for p_id in cd_defense:
                p = []
                plane = self.plane_dao.get_plane_by_plane_id(p_id)
                p.append(plane.get_cockpit())
                body = plane.get_body()
                for bo in body[0]:
                    p.append(bo)
                data["my_defense"].append(p)
            data["my_attacks"] = cd_attacks
            data["opponent_attacks"] = cr_attacks
            opponent = cr
            planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cr_defense]
            my_planes = [self.plane_dao.get_plane_by_plane_id(i) for i in cd_defense]
            messages["attack_messages"] = evaluate_attack(cd_attacks, planes)
            messages["defense_messages"] = evaluate_attack(cr_attacks, my_planes)
        battle_result = self.battle_dao.get_battle_result(battle_id)
        winner = None
        disconnected = None
        if battle_result:
            winner = battle_result[1]
            disconnected = battle_result[2]
        return {'messages': messages, 'data': data, 'params': params,
                'opponent': self.user_dao.get_user_by_id(opponent).get_username(),
                'winner': self.user_dao.get_user_by_id(winner).get_username(), 'disconnected': disconnected}

    def get_battle_history(self, user_id, battle_ids):
        battles = [self.battle_dao.get_battle_by_id(i[0]) for i in battle_ids]
        battles_results = [self.battle_dao.get_battle_result(i[0]) for i in battle_ids]
        i = 0
        data = []
        while i < len(battles_results):
            data.append({'id': battles_results[i][0],
                         'opponent': self.user_dao.get_user_by_id(battles[i].get_challenger_id()).get_username() if
                         battles[i].get_challenged_id() == user_id else
                         self.user_dao.get_user_by_id(battles[i].get_challenged_id()).get_username(),
                         'concludedAt': battles[i].get_end_battle_turn_at(),
                         'defenseSize': battles[i].get_defense_size(),
                         'skySize': battles[i].get_sky_size(),
                         'winner': self.user_dao.get_user_by_id(battles_results[i][1]).get_username()
                         if battles_results[i][1] is not None else 'Unavailable',
                         'disconnected': self.user_dao.get_user_by_id(battles_results[i][2]).get_username()
                         if battles_results[i][2] is not None else 'Unavailable'})
            i += 1

        return data
