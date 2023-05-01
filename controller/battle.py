from flask import Blueprint, request
from exception.busy_player import BusyPlayer
from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from service.battle import BattleService

bc = Blueprint('battle_controller', __name__)
battle_service = BattleService()


@bc.route('/battles', methods=['POST'])
def add_battle():
    # Adds a battle record for a player that already selected battle parameters, their defense, and the maximum
    # amount of time willing to wait for a challenger
    # TO DO get username from read-only cookie and pass it as param to service layer
    user_id = 1
    r_body = request.get_json()
    try:
        max_time = r_body.get('max_time', None)
        defense = r_body.get('defense', None)
        defense_size = r_body.get('defense_size', None)
        sky_size = r_body.get('sky_size', None)
        if defense and defense_size and sky_size and max_time:
            return {"message": battle_service.add_battle(user_id, defense, defense_size, sky_size, max_time)}, 201
        else:
            return "All parameters are required."
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403


@bc.route('/battles/<battle_id>/challengers/defense', methods=['PUT'])
def add_plane_to_battle_defense_by_challenger(battle_id):
    # Adds plane id to challenger's defense array if the user_id, battle_id and plane selection are validated
    r_body = request.get_json()
    # TO DO get user_id from read-only cookie and pass it as param to service layer
    user_id = 2
    try:
        cockpit = r_body.get('cockpit', None)
        flight_direction = r_body.get('flight_direction', None)
        sky_size = r_body.get('sky_size', None)
        if cockpit and flight_direction and sky_size:
            return {"message": battle_service.add_plane_to_battle_defense_by_challenger(battle_id, user_id, cockpit,
                                                                                        flight_direction,
                                                                                        sky_size)}, 200
        else:
            raise InvalidParameter("All parameters are required.")

    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403


@bc.route('/battles/<battle_id>', methods=['PUT'])
def start_battle_by_challenger(battle_id):
    # accepts another player's challenge and sets the defense setup timeframe limit (number of planes = minutes)
    # TO DO get user_id from read-only cookie and pass it as param to service layer
    user_id = 2
    try:
        return {"message": battle_service.start_battle_by_challenger(user_id, battle_id)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403
    except BusyPlayer as e:
        return {"message": str(e)}, 205


@bc.route('/battles/<battle_id>')
def get_battle_status(battle_id):
    # Returns a message based on the user requesting it and the number of attacks for each player in the battle record
    # TO DO get user_id from read-only cookie and pass it as param to service layer
    user_id = 0
    try:
        return {"message": battle_service.get_status(user_id, battle_id)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403


@bc.route('/battles/<battle_id>/attacks', methods=['PUT'])
def update_battle(battle_id):
    # Returns 3 possible messages based choice and its effects on opponents defense (Hit, Miss, Kill)
    user_id = 1
    r_body = request.get_json()
    try:
        attack = r_body.get('attack', None)
        return {"message": battle_service.battle_update(user_id, battle_id, attack)}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403
