import datetime


class Battle:
    def __init__(self, battle_id, challenger_id,	challenged_id, challenger_defense, challenged_defense,
                 sky_size, challenger_attacks, challenged_attacks, rnd_attack_er, rnd_attack_ed, concluded,
                 defense_size, end_battle_turn_at, battle_turn_size):
        self.__battle_id = battle_id
        self.__challenger_id = challenger_id
        self.__challenged_id = challenged_id
        self.__challenger_defense = challenger_defense
        self.__challenged_defense = challenged_defense
        self.__sky_size = sky_size
        self.__challenger_attacks = challenger_attacks
        self.__challenged_attacks = challenged_attacks
        self.__rnd_attack_er = rnd_attack_er
        self.__rnd_attack_ed = rnd_attack_ed
        self.__concluded = concluded
        self.__defense_size = defense_size
        self.__end_battle_turn_at = end_battle_turn_at
        self.__battle_turn_size = battle_turn_size

    def get_battle_id(self):
        return self.__battle_id

    def get_challenger_id(self):
        return self.__challenger_id

    def get_challenged_id(self):
        return self.__challenged_id

    def get_challenger_defense(self):
        return self.__challenger_defense

    def get_challenged_defense(self):
        return self.__challenged_defense

    def get_sky_size(self):
        return self.__sky_size

    def get_challenger_attacks(self):
        return self.__challenger_attacks

    def get_challenged_attacks(self):
        return self.__challenged_attacks

    def get_rnd_attack_er(self):
        return self.__rnd_attack_er

    def get_rnd_attack_ed(self):
        return self.__rnd_attack_ed

    def get_concluded(self):
        return self.__concluded

    def get_defense_size(self):
        return self.__defense_size

    def get_end_battle_turn_at(self):
        return self.__end_battle_turn_at

    def get_battle_turn_size(self):
        return self.__battle_turn_size

    def set_battle_id(self, value):
        self.__battle_id = value

    def set_challenger_id(self, value):
        self.__challenger_id = value

    def set_challenged_id(self, value):
        self.__challenged_id = value

    def set_challenger_defense(self, value):
        self.__challenger_defense = value

    def set_challenged_defense(self, value):
        self.__challenged_defense = value

    def set_sky_size(self, value):
        self.__sky_size = value

    def set_challenger_attacks(self, value):
        self.__challenger_attacks = value

    def set_challenged_attacks(self, value):
        self.__challenged_attacks = value

    def set_rnd_attack_er(self, value):
        self.__rnd_attack_er = value

    def set_rnd_attack_ed(self, value):
        self.__rnd_attack_ed = value

    def set_concluded(self, value):
        self.__concluded = value

    def set_defense_size(self, value):
        self.__defense_size = value

    def set_end_battle_turn_at(self, value):
        self.__end_battle_turn_at = value

    def set_battle_turn_size(self, value):
        self.__battle_turn_size = value

    def check_end_battle_turn_at(self):
        return self.get_end_battle_turn_at().timestamp() > datetime.datetime.now().timestamp()

    def to_dict(self):
        return {
            'battle_id': self.get_battle_id(),
            'challenger_id': self.get_challenger_id(),
            'challenged_id': self.get_challenged_id(),
            'challenger_defense': self.get_challenger_defense(),
            'challenged_defense': self.get_challenged_defense(),
            'sky_size': self.get_sky_size(),
            'challenger_attacks': self.get_challenger_attacks(),
            'challenged_attacks': self.get_challenged_attacks(),
            'rnd_attack_er': self.get_rnd_attack_er(),
            'rnd_attack_ed': self.get_rnd_attack_ed(),
            'concluded': self.get_concluded(),
            'defense_size': self.get_defense_size(),
            'end_battle_turn_at': self.get_end_battle_turn_at(),
            'battle_turn_size': self.get_battle_turn_size()
        }

    def __str__(self):
        return "Battle(id='%s')" % self.get_battle_id()
