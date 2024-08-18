import datetime
import hashlib


def create_password(a, b):
    md5_hashlib = hashlib.new("md5")
    md5_hashlib.update(str(a).encode())
    first_part = str(md5_hashlib.hexdigest())
    md5_hashlib.update(str(b).encode())
    second_part = str(md5_hashlib.hexdigest())
    return first_part + second_part


def confirmation_code_expired(db_time):
    datetime_now = datetime.datetime.now()
    delta = datetime_now - db_time
    return delta.total_seconds() / 60 > 60


def validate_password(password: str) -> tuple[bool, str]:
    special_symbols = ["$", "@", "#", "%"]
    if len(password) < 6:
        return False, "Длина пароля должна быть более 5 символов"
    if len(password) > 20:
        return False, "Длина пароля должна быть менее 21 символа"
    if not any(char.isdigit() for char in password):
        return False, "Пароль должен содержать цифры"
    if not any(char.isupper() for char in password):
        return False, "Пароль должен содержать заглавные буквы"
    if not any(char.islower() for char in password):
        return False, "Пароль должен содержать прописные буквы"
    if not any(char in special_symbols for char in password):
        return False, "Пароль должен содержать специальные символы"
    return True, ""
