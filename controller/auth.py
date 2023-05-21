from flask import Blueprint, request, jsonify
from exception.unauthenticated import Unauthenticated
from service.auth import AuthService
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
import flask

ac = Blueprint('auth_controller', __name__)
auth = AuthService()


@ac.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == "OPTIONS":
        resp = flask.Response("preflight")
        resp.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Content-Length"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
        return resp
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    try:
        user = auth.login(username, password)
        response = jsonify({"msg": "login successful"})
        access_token = create_access_token(identity={"user_id": user.get_user_id(),
                                                     "username": user.get_username()})
        set_access_cookies(response, access_token)

        return response
    except Unauthenticated as e:
        return {
                   "message": str(e)
               }, 401


@ac.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response, 200
