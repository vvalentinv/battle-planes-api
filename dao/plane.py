from dotenv import load_dotenv
from model.plane import Plane
from utilities.db_pool_connection import pool

load_dotenv()


class PlaneDao:

    # uncomment to use with commented route in controller
    # def add_plane(self, plane):
    #     with pool.connection() as conn:
    #         with conn.cursor() as cur:
    #             cur.execute("INSERT INTO planes (cockpit, flight_direction_id, body, sky_size) "
    #                         "VALUES (%s, %s, array[%s], %s) RETURNING *",
    #                         (plane.get_cockpit(), plane.get_flight_direction(),
    #                          plane.get_body(), plane.get_sky_size()))

    def get_plane_id(self, cockpit, flight_direction, sky_size):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM planes WHERE cockpit = %s AND flight_direction_id = %s AND sky_size = %s",
                            (cockpit,  flight_direction, sky_size))
                plane_id = cur.fetchone()
                if plane_id:
                    return plane_id[0]
                return None

    def get_plane_by_plane_id(self, plane_id):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM planes WHERE id = %s ", (plane_id,))
                p = cur.fetchone()
                if p:
                    return Plane(p[0], p[1], p[2], p[3], p[4])
                return None
