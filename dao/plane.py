from dotenv import load_dotenv
import os

import psycopg2

load_dotenv()


class PlaneDao:

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

    def get_plane_id(self, cockpit, flight_direction, sky_size):
        with psycopg2.connect(database=os.getenv("db_name"), user=os.getenv("db_user"),
                              password=os.getenv("db_password"), host=os.getenv("db_host"),
                              port=os.getenv("db_port")) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM planes WHERE cockpit = %s AND flight_direction = %s AND sky_size = %s",
                            (cockpit,  flight_direction, sky_size))
                plane_id = cur.fetchone()
                if plane_id:
                    return int(plane_id[0])
                return None
