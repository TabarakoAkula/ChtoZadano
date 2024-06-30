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
