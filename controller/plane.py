import logging
import traceback

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from exception.invalid_parameter import InvalidParameter
from utilities.helper import build_all_planes_for_sky_size
from service.plane import PlaneService

pc = Blueprint('plane_controller', __name__)
plane_service = PlaneService()


# run only once to build up the planes' table
# @pc.route('/planes/<sky_size>', methods=['POST'])
# def add_all_planes_for_sky_size(sky_size):
#     sky_size = int(sky_size)
#     s_planes = build_all_planes_for_sky_size(sky_size, 4, 2)
#     for p in s_planes:
#         plane_service.add_plane(p)
#     return {"message": f"planes added to database for sky_size = {sky_size}"}, 201


@pc.route('/planes')
@jwt_required()
def get_plane_id():
    r_body = request.get_json()
    try:
        cockpit = r_body.get('cockpit', None)
        flight_direction = r_body.get('direction', None)
        sky_size = r_body.get('sky', None)
        return {"message": plane_service.get_plane_id(cockpit, flight_direction, sky_size)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Exception as e:
        logging.error(traceback.format_exc())
