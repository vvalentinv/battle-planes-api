from flask import Blueprint, request

from exception.forbidden import Forbidden
from model.user import User
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
        added_user = user_service.add_user(User(None, username, password, email))
        return added_user, 200
    except InvalidParameter as e:
        return {
                   "message": str(e)
               }, 400
    except Forbidden as e:
        return {
                   "message": str(e)
               }, 400
