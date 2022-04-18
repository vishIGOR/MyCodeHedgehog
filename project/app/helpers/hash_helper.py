from passlib.context import CryptContext
from random import choice
from string import ascii_letters


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_token():
    return get_random_string(150)


def get_random_string(length: int):
    return "".join(choice(ascii_letters) for _ in range(length))


def hash_password(password: str):
    return PWD_CONTEXT.hash(password)


def validate_password(password: str, hashed_password: str):
    return PWD_CONTEXT.verify(password, hashed_password)
