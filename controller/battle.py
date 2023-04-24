from flask import Blueprint, request

from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from service.battle import BattleService

bc = Blueprint('battle_controller', __name__)
battle_service = BattleService()


@bc.route('/battles/<battle_id>/users/<username>/defense', methods=['POST'])
def add_plane_to_battle_defense_by_username(battle_id, username):
    r_body = request.get_json()
    # TO DO get username from read-only cookie and pass it as param to service layer
    try:
        cockpit = r_body.get('cockpit', None)
        flight_direction = r_body.get('flight_direction', None)
        sky_size = r_body.get('sky_size', None)
        return {"message": battle_service.add_plane_to_battle_defense_by_username(battle_id, username, cockpit,
                                                                                  flight_direction, sky_size)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403


@bc.route('/battles', methods=['POST'])
def add_battle_by_username():
    r_body = request.get_json()
    # TO DO get user_id from read-only cookie and pass it as param to service layer
    user_id = None
    try:
        opponent = r_body.get('opponent', None)
        return {"message": battle_service.add_new_battle(user_id, opponent)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403
