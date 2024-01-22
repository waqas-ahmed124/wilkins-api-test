import os
from datetime import timedelta
from dotenv import load_dotenv

from apiserver.core.security import create_access_token


def generate_cli_user_token():

    access_token_expires = timedelta(days=int(os.environ.get('CLI_USER_TOKEN_EXPIRE_DAYS', 7)))

    data = {
        "sub": f'{os.environ["API_KEY"]}',
        "cli_user": True
    }
    access_token = create_access_token(data=data, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == '__main__':
    load_dotenv(verbose=False)

    resp = generate_cli_user_token()
    print(f'CLI User Token: {resp["access_token"]}')
