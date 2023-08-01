from dotenv import load_dotenv
import os
from psycopg_pool import ConnectionPool

load_dotenv()

database = os.getenv("db_name")
user = os.getenv("db_user")
password = os.getenv("db_password")
host = os.getenv("db_host")
port = os.getenv("db_port")

pool = ConnectionPool(
    'postgresql://' +
    str(user) + ':'
    + str(password) + '@' +
    str(host) + ':' +
    str(port) + '/' +
    str(database)
)
