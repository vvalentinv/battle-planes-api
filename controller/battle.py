from flask import Blueprint, request
from model.battle import Battle
from exception.busy_player import BusyPlayer
from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from service.battle import BattleService

bc = Blueprint('battle_controller', __name__)
battle_service = BattleService()


@bc.route('/battles', methods=['POST'])
def add_battle():
    r_body = request.get_json()
    # TO DO get username from read-only cookie and pass it as param to service layer
    username = None
    try:
        defense = r_body.get('defense', None)
        defense_size = r_body.get('defense_size', None)
        sky_size = r_body.get('sky_size', None)
        if defense and defense_size and sky_size:
            return {"message": battle_service.add_battle(username, defense, defense_size, sky_size)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403


@bc.route('/battles/<battle_id>/challengers/defense', methods=['PUT'])
def add_plane_to_battle_defense_by_username(battle_id):
    r_body = request.get_json()
    # TO DO get username from read-only cookie and pass it as param to service layer
    username = None
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


@bc.route('/battles/<battle_id>', methods=['PUT'])
def start_battle_by_challenger(battle_id):
    # TO DO get user_id from read-only cookie and pass it as param to service layer
    username = None
    try:
        return {"message": battle_service.start_battle_by_challenger(username, battle_id)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403
    except BusyPlayer as e:
        return {"message": str(e)}, 205
