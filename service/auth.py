from dao.user import UserDao
from exception.unauthenticated import Unauthenticated
from utilities.helper import validate_password


class AuthService:

    def __init__(self):
        self.user = UserDao()

    def login(self, username, password):
        user = self.user.get_user_by_username(username)
        if not user:
            raise Unauthenticated('Invalid username or password combination')
        if not validate_password(password, user.get_password()):
            raise Unauthenticated('Invalid username or password combination')
        return user
