from model.user import User
from utilities.helper import hash_registering_password
from dotenv import load_dotenv
import os
import psycopg2


load_dotenv()
os.getenv("ACCESS_KEY")


class UserDao:
    def add_user(self, user):
        h_pass = hash_registering_password(user.get_password().encode('utf-8'))
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (username, pass, email) "
                            "VALUES (%s, %s, %s) RETURNING *", (user.get_username(),  h_pass.decode(), user.get_email()))
                inserted_user = cur.fetchone()
                if inserted_user:
                    return "User successfully added!"
                return None

    def check_for_username(self, username):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT  (SELECT username FROM users WHERE username=%s) = %s", (username, username))
                check = cur.fetchone()
                return check[0]

    def check_for_email(self, email):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT  (SELECT username FROM users WHERE email=%s) = %s", (email, email))
                check = cur.fetchone()
                return check[0]

    def get_user_by_username(self, username):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user:
                    return User(user[0], user[1], user[2], user[3])
                return None

    def update_email(self, username, email):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET email=%s WHERE username=%s RETURNING *", (email, username))
                updated_user = cur.fetchone()
                if updated_user:
                    return "Email successfully updated!"
                return None
    