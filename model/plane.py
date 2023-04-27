class Plane:
    def __init__(self, plane_id, cockpit, flight_direction, body, sky_size):
        self.__plane_id = plane_id
        self.__cockpit = cockpit
        self.__flight_direction = flight_direction
        self.__body = body
        self.__sky_size = sky_size

    def get_plane_id(self):
        return self.__plane_id

    def get_cockpit(self):
        return self.__cockpit

    def get_flight_direction(self):
        return self.__flight_direction

    def get_body(self):
        return self.__body

    def get_sky_size(self):
        return self.__sky_size

    def set_plane_id(self):
        return self.__plane_id

    def set_cockpit(self):
        return self.__cockpit

    def set_flight_direction(self):
        return self.__flight_direction

    def set_body(self):
        return self.__body

    def set_sky_size(self):
        return self.__sky_size

    def to_dict(self):
        return {
            'plane_id': self.get_plane_id(),
            'cockpit': self.get_cockpit(),
            'flight_direction': self.get_flight_direction(),
            'body': self.get_body(),
            'sky_size': self.get_sky_size()
        }

    def __str__(self):
        return "Plane(id='%s')" % self.get_plane_id()
