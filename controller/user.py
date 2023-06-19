import flask
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from exception.forbidden import Forbidden
from exception.invalid_parameter import InvalidParameter
from service.user import UserService

uc = Blueprint('user_controller', __name__)
user_service = UserService()


@uc.route('/users', methods=['POST'])
def add_user():
    r_body = request.get_json()
    try:
        username = r_body.get('username', None)
        password = r_body.get('password', None)
        email = r_body.get('email', None)
        if username and password and email:
            added_user = user_service.add_user(username, password, email)
            return {"message": added_user}, 201
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403


@uc.route('/users', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_user():
    if request.method == "OPTIONS":
        resp = flask.Response("preflight")
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Content-Length, Access-Control-Allow-Credentials"
        resp.headers["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    elif request.method == "PUT":

        r_body = request.get_json()
        user_id = get_jwt_identity().get("user_id")
        try:
            n_pwd = r_body.get('new-password', None)
            password = r_body.get('password', None)
            email = r_body.get('email', None)
            updated_user = user_service.update_user(user_id, password, n_pwd, email)
            return {"message": updated_user}, 200
        except InvalidParameter as e:
            return {"message": str(e)}, 400
        except Forbidden as e:
            return {"message": str(e)}, 403


@uc.route('/users', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_user():
    if request.method == "OPTIONS":
        resp = flask.Response("preflight")
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Content-Length, Access-Control-Allow-Credentials"
        resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp

    elif request.method == "GET":

        return {"username": get_jwt_identity().get('username'),
                "email": get_jwt_identity().get('email')}, 200
