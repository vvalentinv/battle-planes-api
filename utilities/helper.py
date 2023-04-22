import bcrypt


def hash_registering_password(passwd):
    return bcrypt.hashpw(passwd, bcrypt.gensalt())

