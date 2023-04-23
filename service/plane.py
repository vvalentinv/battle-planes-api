from dao.plane import PlaneDao
from model.plane import Plane


class PlaneService:
    def __init__(self):
        self.plane_dao = PlaneDao()
    # uncomment to use with commented route in controller
    # def add_plane(self, p):
    #     # p is a tuple containing plane elements starting with cockpit, sky_size and flight_direction
    #     plane_body = []
    #     for i in range(1, 10):
    #         plane_body.append(p[0][i])
    #     plane = Plane(None, p[0][0], p[2], plane_body, p[1])
    #     self.plane_dao.add_plane(plane)
