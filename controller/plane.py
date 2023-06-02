import logging
import traceback

import flask
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


@pc.route('/planes', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_plane():
    if request.method == "OPTIONS":
        resp = flask.Response("preflight")
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Content-Length, Access-Control-Allow-Credentials"
        resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    elif request.method == "GET":
        args = request.args
        try:
            cockpit = args.get('cockpit', None)
            flight_direction = args.get('direction', None)
            sky_size = args.get('sky', None)
            if cockpit and flight_direction and sky_size:
                return {"message": plane_service.get_plane(cockpit, flight_direction, sky_size)}, 200
        except InvalidParameter as e:
            return {"message": str(e)}, 400
        except Exception as e:
            logging.error(traceback.format_exc())
