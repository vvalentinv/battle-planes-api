from dao.battle import BattleDao


class BattleService:
    def __init__(self):
        self.battle_dao = BattleDao()
