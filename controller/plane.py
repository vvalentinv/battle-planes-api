from flask import Blueprint, request
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



