class User:
    def __init__(self, user_id, username, password, email):
        self.__user_id = user_id
        self.__username = username
        self.__password = password
        self.__email = email

    def get_user_id(self):
        return self.__user_id

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_email(self):
        return self.__email

    def set_password(self, value):
        self.__password = value

    def set_email(self, value):
        self.__email = value

    def to_dict(self):
        return {
            'user_id': self.get_user_id(),
            'username': self.get_username(),
            'password': self.get_password(),
            'email': self.get_email()
        }

    def __str__(self):
        return "User(id='%s')" % self.get_user_id()
