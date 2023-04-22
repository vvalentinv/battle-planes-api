from dao.user import UserDao
from exception.forbidden import Forbidden
from utilities.helper import validate_password


class UserService:
    def __init__(self):
        self.user_dao = UserDao()

    def add_user(self,  user):
        # TO DO validate values
        if self.user_dao.check_for_username(user.get_username()):
            raise Forbidden("This username is already in use! Please try again.")
        if self.user_dao.check_for_email(user.get_email()):
            raise Forbidden("This email is already in use! Please sign into your existing account.")
        return self.user_dao.add_user(user)

    def update_email(self, username, password, email):
        # TO DO validate email, password values
        if not validate_password(password, self.user_dao.get_user_by_username(username).get_password()):
            raise Forbidden("Invalid password for this account!")
        return self.user_dao.update_email(username, email)



