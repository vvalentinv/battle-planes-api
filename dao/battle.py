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

    def add_battle(self, user, opponent):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO battles (challenger_id, challenged_id) "
                            "VALUES (%s, %s)", (user.get_user_id(), opponent.get_user_id()))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return "Challenge accepted!"
                return None
