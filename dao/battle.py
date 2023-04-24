from dotenv import load_dotenv
import os

import psycopg2

load_dotenv()


class BattleDao:
    def __init__(self):
        self.check_if_user_is_battle_ready = None

    def add_plane_to_battle_defense_by_username(self, battle_id, planes_array, username):
        pass

    def get_defense_position(self, battle_id, username):
        pass

    def get_defense_by_id_username_and_position(self, battle_id, username, position):
        pass

    def add_battle(self, user_id, opponent_id):
        pass
