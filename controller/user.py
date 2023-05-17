from flask import Blueprint, request

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


@uc.route('/users/', methods=['PUT'])
def update_user():
    # TO DO check if the signed-in user is the owner of the account to be changed
    # TO DO get user_id from identity
    r_body = request.get_json()
    user_id = 1
    try:
        n_pwd = r_body.get('new_password', None)
        password = r_body.get('password', None)
        email = r_body.get('email', None)
        updated_user = user_service.update_user(user_id, password, n_pwd, email)
        return {"message": updated_user}, 200
    except InvalidParameter as e:
        return {"message": str(e)}, 400
    except Forbidden as e:
        return {"message": str(e)}, 403


