from dotenv import load_dotenv
from model.battle import Battle
from utilities.db_pool_connection import pool

load_dotenv()


class BattleDao:

    def add_planes_to_battle_defense_by_username(self, battle_id, plane_ids_array):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_defense=%s WHERE id=%s RETURNING *"
                            , (plane_ids_array, battle_id))
                b = cur.fetchone()
                if b:
                    battle = Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], b[10], b[11],
                                    b[12], b[13])
                    curr_def = battle.get_challenger_defense() or []
                    turn_time = str(battle.get_battle_turn_size()) + ' MINUTE'
                    if battle.get_defense_size() == len(curr_def):
                        cur.execute("UPDATE battles SET end_battle_turn_at = Now() + %s "
                                    " WHERE id=%s RETURNING *"
                                    , (turn_time, battle_id))
                    else:
                        cur.execute("UPDATE battles SET end_battle_turn_at = Now() + '1 MINUTE'  WHERE id=%s "
                                    "RETURNING *"
                                    , (battle_id, ))
                    return f"{battle.get_defense_size() - len(curr_def)} more plane(s) to add " \
                           f"until defense setup is complete."
                return None

    def add_challenger_to_battle(self, user_id, battle_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_id=%s, end_battle_turn_at = Now() + '1 MINUTE' "
                            "WHERE id=%s RETURNING *"
                            , (user_id, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return "Challenge accepted!"
                return None

    def get_battle_by_id(self, battle_id):
        battle_id = int(battle_id)
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM battles WHERE id = %s", (battle_id,))
                b = cur.fetchone()
                if b:
                    return Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8], b[9], b[10], b[11],
                                  b[12], b[13])
                return None

    def add_battle(self, battle, max_time, turn_time):
        max_time = str(max_time) + ' MINUTE'
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO battles (challenger_id, challenged_id, challenged_defense, sky_size, concluded, "
                    "defense_size, end_battle_turn_at, battle_turn_size) "
                    "VALUES	(0, %s, %s, %s, False, %s, Now() + %s, %s) RETURNING *",
                    (battle.get_challenged_id(), battle.get_challenged_defense(), battle.get_sky_size(),
                     battle.get_defense_size(), max_time, turn_time))
                b = cur.fetchone()
                if b:
                    return b[0], b[12]
                return "db error", "db error"

    def is_engaged(self, user_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM battles "
                            "WHERE concluded IS False AND challenger_id = %s "
                            # "AND Now() < end_battle_turn_at "
                            "UNION "
                            "SELECT id FROM battles "
                            "WHERE concluded IS False AND challenged_id = %s "
                            # "AND challenger_id <> 0 AND Now() < end_battle_turn_at "
                            , (user_id, user_id))
                found = cur.fetchone()
                if found:
                    return found[0]
                return False

    def is_time_left(self, battle_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT (SELECT end_battle_turn_at FROM battles WHERE id = %s) >= Now()", (battle_id,))
                found = cur.fetchone()
                if found:
                    return found[0]

    def is_concluded(self, battle_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT concluded FROM battles WHERE id = %s", (battle_id,))
                found = cur.fetchone()
                if found:
                    return found[0]

    def add_challenger_attacks_to_battle(self, battle_id, attacks, turn_time='3 MINUTE'):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenger_attacks=%s, end_battle_turn_at = Now() + %s "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def add_challenged_attacks_to_battle(self, battle_id, attacks, turn_time='3 MINUTE'):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET challenged_attacks=%s, end_battle_turn_at = Now() + %s "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def conclude_unchallenged_battles(self, user_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True "
                            "WHERE challenged_id = %s AND challenger_id=0"
                            , (user_id,))
                return True

    def add_random_challenger_attacks_to_battle(self, battle_id, attacks, turn_time='3 MINUTE'):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET rnd_attack_er=%s, end_battle_turn_at = Now() + %s "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def add_random_challenged_attacks_to_battle(self, battle_id, attacks, turn_time='3 MINUTE'):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET rnd_attack_ed=%s, end_battle_turn_at = Now() + %s "
                            "WHERE id=%s RETURNING *"
                            , (attacks, turn_time, battle_id))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return True
                return None

    def conclude_unfinished_battle(self, battle_id, disconnected_user):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, end_battle_turn_at = Now() "
                            "WHERE id = %s RETURNING *"
                            , (battle_id,))
                b = cur.fetchone()
                if b:
                    cur.execute("INSERT INTO battle_results (battle_id, disconnected_user) VALUES (%s, %s) RETURNING *",
                                (battle_id, disconnected_user))
                    if cur.fetchone():
                        return True

    def conclude_unfinished_defense_setup_battle(self, battle_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, end_battle_turn_at = Now()::date "
                            "WHERE id = %s"
                            , (battle_id,))
                return True

    def conclude_user_conceded_battles(self, user_id, battle_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, end_battle_turn_at = Now() "
                            "WHERE id = %s Returning *", (battle_id,))
                b = cur.fetchone()
                if b:
                    battle = Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8],
                                    b[9], b[10], b[11], b[12], b[13])
                    if battle.get_challenger_id() == user_id:
                        winner = battle.get_challenged_id()
                    else:
                        winner = battle.get_challenger_id()
                    cur.execute("INSERT INTO battle_results (battle_id, winner) VALUES (%s, %s) RETURNING *",
                                (battle_id, winner))
                    if cur.fetchone():
                        return battle, winner

    def conclude_unstarted_battle(self):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, end_battle_turn_at = Now()::date "
                            "WHERE coalesce(array_length(challenger_defense, 1), 0) < defense_size "
                            "AND end_battle_turn_at < Now() "
                            )
                return True

    def conclude_won_battle(self, battle_id, winner):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE battles SET concluded = True, end_battle_turn_at = Now() "
                            "WHERE id = %s RETURNING *"
                            , (battle_id,))
                if cur.fetchone():
                    cur.execute("INSERT INTO battle_results (battle_id, winner) VALUES (%s, %s) RETURNING *",
                                (battle_id, winner))
                    return True

    def get_unchallenged_battles(self):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM battles "
                            "WHERE challenger_id = 0 AND end_battle_turn_at > Now() AND "
                            "concluded = False", )
                b = cur.fetchone()
                battles = []
                while b:
                    battles.append(Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8],
                                          b[9], b[10], b[11], b[12], b[13]))
                    b = cur.fetchone()
                return battles

    def get_defense_setup_for_challenger(self, user_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM battles WHERE challenger_id = %s and "
                            "coalesce(array_length(challenger_defense, 1), 0) < defense_size and concluded = False",
                            (user_id,))
                b = cur.fetchone()
                if b:
                    return Battle(b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8],
                                  b[9], b[10], b[11], b[12], b[13])
                else:
                    return None

    def get_battle_id_list(self, user_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT b.id FROM battles b JOIN battle_results br ON b.id = br.battle_id "
                            "WHERE (challenger_id = %s OR challenged_id = %s) AND "
                            "coalesce(array_length(challenger_defense, 1), 0) = defense_size AND concluded = True",
                            (user_id, user_id))
                b_id = cur.fetchone()
                result = []
                while b_id:
                    result.append(b_id)
                    b_id = cur.fetchone()
                return result

    def get_battle_result(self, battle_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT battle_id, winner, disconnected_user FROM battle_results WHERE battle_id = %s",
                            (battle_id,))
                result = cur.fetchone()
                if result:
                    return result[0], result[1], result[2]
                return None
