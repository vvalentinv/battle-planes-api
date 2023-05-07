from dotenv import load_dotenv
import os
from model.battle import Battle
import psycopg2

load_dotenv()


class BattleDao:

    def add_plane_to_battle_defense_by_username(self, battle_id, planes_array):
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
                    return "You have set your defense and waiting for a challenger!"
                return None

    def is_engaged(self, user_id):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT (SELECT challenger_id FROM battles "
                            "WHERE concluded IS False AND challenger_id = %s "
                            "UNION "
                            "SELECT challenged_id FROM battles WHERE concluded IS False AND challenged_id = %s AND "
                            "challenger_id <> 0 ) "
                            " = %s", (user_id, user_id, user_id))
                found = cur.fetchone()
                if found and found[0]:
                    return True
                elif found and found[0] == "NULL":
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
        print(attacks)
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_attacks=%s, battle_turn = Now() + '%s MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    print(inserted_user)
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
