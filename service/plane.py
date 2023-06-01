from dao.plane import PlaneDao
from exception.invalid_parameter import InvalidParameter
from model.plane import Plane
from service.input_validation_helper import validate_int, validate_flight_direction


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
    def get_plane_id(self, cockpit, flight_direction, sky_size):
        if validate_int(cockpit) and validate_int(sky_size) and validate_flight_direction(
                flight_direction) and 9 < sky_size < 16:
            plane_id = self.plane_dao.get_plane_id(cockpit, flight_direction, sky_size)
            if plane_id is not None:
                return plane_id
            else:
                raise InvalidParameter("No match")
