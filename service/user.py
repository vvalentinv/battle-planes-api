from dao.user import UserDao
from exception.forbidden import Forbidden
from model.user import User
from utilities.input_validation_helper import validate_password, validate_username, validate_email, \
    validate_password_value


class UserService:
    def __init__(self):
        self.user_dao = UserDao()

    def add_user(self, username, password, email):
        if validate_username(username) and \
                validate_email(email) and validate_password_value(password):
            pass
        if self.user_dao.check_for_username(username):
            raise Forbidden("This username is already in use! Please try again.")
        if self.user_dao.check_for_email(email):
            raise Forbidden("This email is already in use! Please sign into your existing account.")
        return self.user_dao.add_user(User(None, username, password, email))

    def update_user(self, username, password, n_pwd, email):
        if email is not None:
            if validate_email(email):
                pass
            if not validate_password(password, self.user_dao.get_user_by_username(username).get_password()):
                raise Forbidden("Invalid password for this account!")
            return self.user_dao.update_email(username, email)
        elif validate_password_value(n_pwd):
            pass
            if not validate_password(password, self.user_dao.get_user_by_username(username).get_password()):
                raise Forbidden("Invalid password for this account!")
            return self.user_dao.update_password(username, n_pwd)





