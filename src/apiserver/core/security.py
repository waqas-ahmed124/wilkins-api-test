import os
import time
from datetime import timedelta

from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = time.time() + expires_delta.total_seconds()

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.environ['SECRET_KEY'], algorithm=os.environ['ALGORITHM'])

    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
