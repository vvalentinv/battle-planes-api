import datetime

from dotenv import load_dotenv
import os
from model.battle import Battle
import psycopg2

load_dotenv()


class BattleDao:

    def add_planes_to_battle_defense_by_username(self, battle_id, planes_array):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_defense=%s WHERE id=%s RETURNING *"
                            , (planes_array, battle_id))
                b = cur.fetchone()
                if b:
                    battle = Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], b[10], b[11], b[12])
                    curr_def = battle.get_challenger_defense() or []
                    if battle.get_defense_size() == len(curr_def):
                        return "Defense setup complete!"
                    return f"{battle.get_defense_size() - len(curr_def)} more plane(s) to add " \
                           f"until defense setup is complete."
                return None

    def add_challenger_to_battle(self, user_id, battle_id, defense_size):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_id=%s, battle_turn = Now() + '%s MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (user_id, defense_size, battle_id))
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
                    return Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], b[10], b[11], b[12])
                return None

    def add_battle(self, battle, max_time):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO battles (challenger_id, challenged_id, challenged_defense, concluded, battle_turn) "
                    "VALUES	(0, %s, %s, False, Now() + '%s MINUTE') returning *",
                    (battle.get_challenged_id(), battle.get_challenged_defense(), max_time))
                b = cur.fetchone()
                if b:
                    return b[0], b[12]
                return "db error", "db error"

    def is_engaged(self, user_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM battles "
                            "WHERE concluded IS False AND challenger_id = %s "
                            "AND Now() < battle_turn + '1 MINUTE' "
                            "UNION "
                            "SELECT id FROM battles "
                            "WHERE concluded IS False AND challenged_id = %s AND "
                            "challenger_id <> 0 AND Now() < battle_turn + '1 MINUTE'", (user_id, user_id))
                found = cur.fetchone()
                if found:
                    return found[0]
                return False

    def is_time_left(self, battle_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT (SELECT battle_turn FROM battles WHERE id = %s) >= Now()", (battle_id,))
                found = cur.fetchone()
                if found:
                    return found[0]

    def is_concluded(self, battle_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT concluded FROM battles WHERE id = %s", (battle_id,))
                found = cur.fetchone()
                if found:
                    return found[0]

    def add_challenger_attacks_to_battle(self, battle_id, attacks, turn_time=3):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_attacks=%s, battle_turn = Now() + '%s MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def add_challenged_attacks_to_battle(self, battle_id, attacks, turn_time=3):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenged_attacks=%s, battle_turn = Now() + '%s MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def conclude_unchallenged_battles(self, user_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True "
                            "WHERE challenged_id = %s AND challenger_id=0"
                            , (user_id,))
                return True

    def add_random_challenger_attacks_to_battle(self, battle_id, attacks, turn_time=3):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET rnd_attack_er=%s, battle_turn = Now() + '%s MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def add_random_challenged_attacks_to_battle(self, battle_id, attacks, turn_time=3):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET rnd_attack_ed=%s, battle_turn = Now() + '%s MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def conclude_unfinished_battle(self, battle_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, battle_turn = Now()::date "
                            "WHERE id = %s"
                            , (battle_id,))
                return True

    def conclude_user_unfinished_battles(self, user_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, battle_turn = Now()::date "
                            "WHERE battle_turn + '1 MINUTE' < Now() AND " 
                            "((challenger_id = %s AND coalesce(array_length(challenger_defense, 1), 0) = defense_size) "
                            "OR (challenged_id = %s AND challenger_id <> 0)) "
                            , (user_id, user_id))
                return True

    def conclude_unstarted_battle(self):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, battle_turn = Now()::date "
                            "WHERE coalesce(array_length(challenger_defense, 1), 0) < defense_size "
                            "AND battle_turn < Now() "
                            )
                return True

    def conclude_won_battle(self, battle_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, battle_turn = Now() "
                            "WHERE id = %s"
                            , (battle_id,))
                print("won")
                return True

    def get_unchallenged_battles(self, user_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM battles "
                            "WHERE challenger_id = 0 AND battle_turn > Now() AND "
                            "concluded = False",)
                b = cur.fetchone()
                battles = []
                while b:
                    battles.append(Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8],
                                          b[9], b[10], b[11], b[12]))
                    b = cur.fetchone()
                return battles

    def get_defense_setup_for_challenger(self, user_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM battles WHERE challenger_id = %s and "
                            "coalesce(array_length(challenger_defense, 1), 0) < defense_size and concluded = False",
                            (user_id, ))
                b = cur.fetchone()
                if b:
                    return Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8],
                                          b[9], b[10], b[11], b[12])
                else:
                    return None

    def get_battle_id_list(self, user_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM battles WHERE (challenger_id = %s OR challenged_id = %s) AND "
                            "coalesce(array_length(challenger_defense, 1), 0) = defense_size AND concluded = True",
                            (user_id, user_id))
                b_id = cur.fetchone()
                result = []
                while b_id:
                    result.append(b_id)
                    b_id = cur.fetchone()
                return result
