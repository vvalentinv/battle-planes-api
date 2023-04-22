from dao.user import UserDao
from exception.forbidden import Forbidden


class UserService:
    def __init__(self):
        self.user_dao = UserDao()

    def add_user(self, user):
        if self.user_dao.get_user_by_username(user.username):
            raise Forbidden("This username is already in use! Please try again.")
        if self.user_dao.get_user_by_email(user.email):
            raise Forbidden("This email is already in use! Please sign into your existing account.")
        added_user_obj = self.user_dao.add_user(user)
        return added_user_obj.to_dict()
