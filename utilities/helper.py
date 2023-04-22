import bcrypt


def hash_registering_password(passwd):
    return bcrypt.hashpw(passwd, bcrypt.gensalt())

def validate_password(passwd, hash):
    return bcrypt.checkpw(passwd.encode(), hash.encode())
