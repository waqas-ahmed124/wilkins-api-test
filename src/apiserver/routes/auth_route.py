import os
import time

import httpx
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import timedelta
from typing import Any, Annotated
from fastapi_sqlalchemy import db
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose.exceptions import JWTClaimsError

from apiserver.models import User
from apiserver.schemas import UserAuthenticate, SignInResponse, Token
from apiserver.core.security import verify_password, create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

CACHED_PUBLIC_KEYS = {}


class AuthRouter:
    @property
    def router(self):
        api_router = APIRouter(prefix="/auth", tags=["Auth"])

        @api_router.post("/sign-in", status_code=200, response_model=SignInResponse)
        def sign_in(form_data: UserAuthenticate) -> Any:
            user = db.session.query(User).filter(User.email == form_data.email).one_or_none()

            if not user or not verify_password(form_data.password, user.password):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            access_token_expires = timedelta(hours=int(os.environ.get('ACCESS_TOKEN_EXPIRE_HOURS', 24)))

            access_token = create_access_token(data={"sub": f'{user.id}'}, expires_delta=access_token_expires)

            resp = {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "is_admin": user.is_admin
                }
            }

            return resp

        @api_router.post("/token", response_model=Token, include_in_schema=False)
        async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
            user = authenticate_user(form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            access_token_expires = timedelta(hours=int(os.environ.get('ACCESS_TOKEN_EXPIRE_HOURS', 24)))

            access_token = create_access_token(data={"sub": f'{user.id}'}, expires_delta=access_token_expires)

            return {"access_token": access_token, "token_type": "bearer"}

        return api_router


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=os.environ['ALGORITHM'])
        subject = payload.get("sub")
        cli_user = payload.get("cli_user", False)

        if subject is None:
            raise credentials_exception

        # Check token expiration
        expiration_time = payload.get("exp")
        if expiration_time is not None:
            now = time.time()
            if expiration_time < now:
                raise credentials_exception

    except JWTError:
        raise credentials_exception

    if cli_user:
        if subject != os.environ['API_KEY']:
            raise credentials_exception
    else:
        user = db.session.query(User).get(subject)
        if user is None:
            raise credentials_exception

    if cli_user:
        user_obj = {
            'user_id': 0,
            'name': 'cli_user',
            'email': 'cli_user',
            'is_admin': False,
            'is_cli_user': True
        }
    else:
        user_obj = {
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'is_admin': user.is_admin,
            'is_cli_user': False
        }

    return user_obj


async def get_azure_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        kid = get_token_kid(token)
        key = get_public_key(kid)

        payload = jwt.decode(token,
                             key=key,
                             algorithms=os.environ['AZURE_ALGORITHM'],
                             # audience=os.environ['APP_CLIENT_ID'],
                             # issuer=f'https://login.microsoftonline.com/{os.environ["TENANT_ID"]}/v2.0'
                             audience=f"api://{os.environ['APP_CLIENT_ID']}",
                             issuer=f'https://sts.windows.net/{os.environ["TENANT_ID"]}/')

    except JWTClaimsError as e:
        print(f'The token has some invalid claims: {e}')
        credentials_exception.detail = f'The token has some invalid claims: {e}'
        raise credentials_exception
    except ExpiredSignatureError:
        print("The token signature has expired!")
        credentials_exception.detail = "The token signature has expired!"
        raise credentials_exception
    except JWTError:
        print("The token is invalid!")
        credentials_exception.detail = "The token is invalid!"
        raise credentials_exception
    except Exception:
        print("Unable to decode token!")
        credentials_exception.detail = "Unable to decode token!"
        raise credentials_exception

    '''
    appidacr: Indicates how the client was authenticated. 
    0: For a public client, the value is "0". 
    1: If client ID and client secret are used, the value is "1". (CLI User)
    2: If a client certificate was used for authentication, the value is "2".
    '''

    try:
        user_obj = {
            'user_id': payload['oid'],
            'name': payload.get('name'),
            'email': payload.get('email'),
            'is_admin': False,
            'is_cli_user': True if payload['appidacr'] == "1" else False
        }
    except Exception:
        print("Unable to extract user details from token!")
        credentials_exception.detail = "Unable to extract user details from token!"
        raise credentials_exception

    return user_obj


def get_public_key(kid) -> dict:
    if kid in CACHED_PUBLIC_KEYS:
        return CACHED_PUBLIC_KEYS[kid]

    else:
        tenant_id = os.environ['TENANT_ID']
        app_client_id = os.environ['APP_CLIENT_ID']

        try:
            response = httpx.get(f'https://login.microsoftonline.com/{tenant_id}/discovery/keys?appid={app_client_id}')
            response.raise_for_status()
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to fetch Public Key",
                                headers={"WWW-Authenticate": "Bearer"},)

        keys = response.json()

        for key in keys['keys']:
            CACHED_PUBLIC_KEYS[key['kid']] = key

        return CACHED_PUBLIC_KEYS[kid]


def get_token_kid(token) -> str:
    unverified_header = jwt.get_unverified_header(token)
    return unverified_header['kid']


def authenticate_user(email: str, password: str):
    user = db.session.query(User).filter(User.email == email).one_or_none()

    if user is None:
        return False

    if not verify_password(password, user.password):
        return False

    return user


async def is_cli_user(token: Annotated[str, Depends(oauth2_scheme)]) -> bool:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=os.environ['ALGORITHM'])
        api_key: str = payload.get("sub")
        cli_user: bool = payload.get("cli_user", False)

        if api_key is None or cli_user is None:
            raise credentials_exception

        if api_key != os.environ['API_KEY'] or not cli_user:
            raise credentials_exception

        # Check token expiration
        expiration_time = payload.get("exp")
        if expiration_time is not None:
            now = time.time()
            if expiration_time < now:
                raise credentials_exception

    except JWTError:
        raise credentials_exception

    return True
