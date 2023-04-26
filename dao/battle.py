from dotenv import load_dotenv
import os
from model.battle import Battle
import psycopg2

load_dotenv()


class BattleDao:

    def add_plane_to_battle_defense_by_username(self, battle_id, planes_array, username):
        pass

    def get_defense_position(self, battle_id, username):
        pass

    def get_defense_by_id_username_and_position(self, battle_id, username, position):
        pass

    def add_challenger_to_battle(self, user, battle_id, defense_size):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_id=%s AND battle_turn = Now() + '%s MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (user.get_user_id(), defense_size, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return "Challenge accepted!"
                return None

    def get_battle_by_id(self, battle_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM battles WHERE id = %s", (battle_id,))
                b = cur.fetchone()
                if b:
                    return Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], b[10], b[11])
                return None

    def check_challenger_id(self, battle_id, param):
        pass

    def add_battle(self, battle):
        pass
