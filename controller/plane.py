from flask import Blueprint, request

pc = Blueprint('plane_controller', __name__)

#run only once to build up the planes table
@pc.route('/planes', methods=['POST'])
def add_all_planes_for_all_sky_sizes():
    pass
