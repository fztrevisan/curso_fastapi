from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.settings import Settings

pwd_context = PasswordHash.recommended()
oath2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
settings = Settings()


def get_password_hash(password: str) -> str:
    """
    Hashes a password for storing.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a stored password against one provided by user.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oath2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate the provided credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(
            token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email: str = payload.get('sub')
        if not email:
            raise credentials_exception

    except ExpiredSignatureError:
        credentials_exception.detail = 'Expired token'
        raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = session.scalar(select(User).where(User.email == email))
    if not user:
        raise credentials_exception

    return user
