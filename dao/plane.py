from dotenv import load_dotenv
import os

import psycopg2

load_dotenv()


class PlaneDao:
    pass
    # uncomment to use with commented route in controller
    # def add_plane(self, plane):
    #     with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
    #                           password=os.getenv("db_password"), host=os.getenv("db_host"),
    #                           port=os.getenv("db_port")) as conn:
    #         with conn.cursor() as cur:
    #             cur.execute("INSERT INTO planes (cockpit, flight_direction, body, sky_size) "
    #                         "VALUES (%s, %s, array[%s], %s) RETURNING *",
    #                         (plane.get_cockpit(), plane.get_flight_direction(),
    #                          plane.get_body(), plane.get_sky_size()))

