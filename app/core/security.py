def get_password_hash(password: str) -> str:
    return password + "_hashed"


def verify_password(password, hashed_password) -> bool:
    return password == hashed_password
