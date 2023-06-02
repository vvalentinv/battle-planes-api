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
    def get_plane(self, cockpit, flight_direction, sky_size):
        plane_data = {"id": "", "plane": []}
        if validate_int(sky_size):
            sky = int(sky_size)
        if validate_int(cockpit) and validate_flight_direction(
                flight_direction) and 9 < sky < 16:
            plane_id = self.plane_dao.get_plane_id(cockpit, flight_direction, sky_size)
            if plane_id is None:
                plane_data["id"] = "No match"
            else:
                plane_data["id"] = plane_id
                plane = self.plane_dao.get_plane_by_plane_id(plane_id)
                plane_data["plane"].append(plane.get_cockpit())
                body = plane.get_body()
                for b in body[0]:
                    plane_data["plane"].append(b)
            return plane_data
