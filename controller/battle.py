import traceback

import flask
from flask import Blueprint, request, logging
from flask_jwt_extended import jwt_required, get_jwt_identity

from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from service.battle import BattleService
from service.user import UserService

bc = Blueprint('battle_controller', __name__)
battle_service = BattleService()
user_service = UserService()

@bc.route('/battles', methods=['POST', 'OPTIONS'])
@jwt_required()
def add_battle():
    # Adds a battle record for a player that already selected battle parameters, their defense, and the maximum
    # amount of time willing to wait for a challenger
    # TO DO get username from read-only cookie and pass it as param to service layer
    if request.method == "OPTIONS":
        resp = flask.Response("preflight")
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Content-Length, Access-Control-Allow-Credentials"
        resp.headers["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    elif request.method == "POST":
        req_id = get_jwt_identity()
        r_body = request.get_json()
        try:
            max_time = r_body.get('max-time', None)
            defense = r_body.get('defense', None)
            defense_size = r_body.get('defense-size', None)
            sky_size = r_body.get('sky-size', None)
            if defense and defense_size and sky_size and max_time:
                opened_challenge = battle_service.add_battle(req_id.get("user_id"), defense,
                                                             defense_size, sky_size, max_time)
                return {"timeStamp": opened_challenge[1], "battleId": opened_challenge[0]}, 201
            else:
                return {"message": "All parameters are required."}, 400
        except InvalidParameter as e:
            return {"message": str(e)}, 400
        except Forbidden as e:
            return {"message": str(e)}, 403


@bc.route('/battles/<battle_id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_battle(battle_id):
    # Adds plane id to challenger's defense array if the user_id, battle_id and plane selection are validated
    # TO DO get user_id from read-only cookie and pass it as param to service layer
    if request.method == "OPTIONS":
        resp = flask.Response("preflight")
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Content-Length, Access-Control-Allow-Credentials"
        resp.headers["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    elif request.method == "PUT":
        user_id = get_jwt_identity().get("user_id")
        r_body = request.get_json(silent=True)
        args = request.args
        try:
            defense = args.get('defense')
            accepted = args.get('accepted')
            attack = args.get('attack')
            if not len(args) == 1:
                raise InvalidParameter("Only one query parameter is expected!")
        except InvalidParameter as e:
            return {"message": str(e)}, 400
        try:
            if defense:
                cockpit = r_body.get('cockpit', None)
                flight_direction = r_body.get('direction', None)
                sky_size = r_body.get('sky', None)
                if cockpit and flight_direction and sky_size:
                    return {"message": battle_service.add_plane_to_battle_defense_by_challenger(battle_id, user_id,
                                                                                                cockpit,
                                                                                                flight_direction,
                                                                                                sky_size)}, 200
                else:
                    raise InvalidParameter("All parameters are required.")
            elif accepted:
                return {"message": battle_service.start_battle_by_challenger(user_id, battle_id)}, 200
            elif attack:
                attack = r_body.get('attack', None)
                return {"messages": battle_service.battle_update(user_id, battle_id, attack)}, 200
            else:
                raise InvalidParameter("Unknown parameter")
        except InvalidParameter as e:
            return {"message": str(e)}, 400
        except Forbidden as e:
            return {"message": str(e)}, 403


@bc.route('/battles')
@jwt_required()
def get_unchallenged_battles_or_battle_status():
    # accepts another player's challenge and sets the defense setup timeframe limit (number of planes = minutes)
    # TO DO get user_id from read-only cookie and pass it as param to service layer
    user_id = get_jwt_identity().get("user_id")
    args = request.args
    try:
        history = args.get('history', None)
        defeat_status = args.get('defeat', None)
        battle_id = battle_service.battle_dao.is_engaged(user_id)
        battles = battle_service.battle_dao.get_battle_id_list(user_id)
        opponent_id = None
        if battle_id:
            b = battle_service.battle_dao.get_battle_by_id(battle_id)
            if b.get_challenger_id() == user_id:
                opponent_id = b.get_challenged_id()
            else:
                opponent_id = b.get_challenger_id()

        if battle_id and defeat_status:
            return {"status": battle_service.get_status(user_id, battle_id, defeat_status),
                    "user": get_jwt_identity().get('username'),
                    "battleID": battle_id,
                    "opponent": user_service.user_dao.get_user_by_id(opponent_id).get_username()}, 200
        elif history:
            if history == 'all':
                return {"history": battle_service.get_battle_history(user_id, battles)}, 200
            elif history == "last":
                return {"outcome": battle_service.get_battle_result(user_id, battle_id)}, 200
        else:
            battle_service.battle_dao.conclude_user_unfinished_battles(user_id)
            return {"battles": battle_service.get_unchallenged_battles(user_id),
                    "user": get_jwt_identity().get('username')}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403

# @bc.route('/battles/<battle_id>')
# @jwt_required()
# def get_battle_status(battle_id):
#     # Returns a battle data for the user
#     # TO DO get user_id from read-only cookie and pass it as param to service layer
#     user_id = get_jwt_identity().get("user_id")
#     try:
#         return {"message": battle_service.get_status(user_id, battle_id)}, 200
#     except InvalidParameter as e:
#         return {"message": str(e)}, 400
#     except Forbidden as e:
#         return {"message": str(e)}, 403

#
# @bc.route('/battles/<battle_id>/attacks', methods=['PUT'])
# def update_battle(battle_id):
#     # Returns a tuple array of the attack and  one of (Hit, Miss, Kill)
#     user_id = 2
#     r_body = request.get_json()
#     try:
#         attack = r_body.get('attack', None)
#         return {"messages": battle_service.battle_update(user_id, battle_id, attack)}, 200
#     except InvalidParameter as e:
#         return {"message": str(e)}, 400
#     except Forbidden as e:
#         return {"message": str(e)}, 403
