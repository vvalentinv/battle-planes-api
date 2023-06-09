from model.user import User
from utilities.db_pool_connection import pool
from utilities.helper import hash_registering_password
from dotenv import load_dotenv

load_dotenv()


class UserDao:
    def add_user(self, user):
        h_pass = hash_registering_password(user.get_password().encode('utf-8'))
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (username, pass, email) "
                            "VALUES (%s, %s, %s) RETURNING *", (user.get_username(),  h_pass.decode(), user.get_email()))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return "User successfully added!"
                return None

    def check_for_username(self, username):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT (SELECT username FROM users WHERE username=%s) = %s", (username, username))
                check = cur.fetchone()
                return check[0]

    def check_for_email(self, email):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT (SELECT email FROM users WHERE email=%s) = %s", (email, email))
                check = cur.fetchone()
                return check[0]

    def get_user_by_username(self, username):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user:
                    return User(user[0], user[1], user[2], user[3])
                return None

    def get_user_by_id(self, user_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                if user:
                    return User(user[0], user[1], user[2], user[3])
                return None

    def update_email(self, user_id, email):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET email=%s WHERE id=%s RETURNING *", (email, user_id))
                updated_user = cur.fetchone()
                if updated_user:
                    return "Email successfully updated!"
                return None


    def update_password(self, user_id, n_pwd):
        h_pass = hash_registering_password(n_pwd.encode('utf-8'))
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET pass=%s WHERE id=%s RETURNING *", (h_pass.decode(), user_id))
                updated_user = cur.fetchone()
                if updated_user:
                    return "Password successfully updated!"
                return None
    