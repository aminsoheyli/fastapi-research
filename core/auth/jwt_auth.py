import datetime
import time
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.users.models import UserModel

security = HTTPBearer(scheme_name="Token")

from fastapi.security import HTTPBearer

from core.config import settings

security = HTTPBearer(scheme_name="Token")

ACCESS_TOKEN_EXPIRY = int(datetime.timedelta(minutes=5).total_seconds())
REFRESH_TOKEN_EXPIRY = int(datetime.timedelta(days=1).total_seconds())


def get_jwt_token_authenticated_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        db: Annotated[Session, Depends(get_db)]
):
    token = credentials.credentials

    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed, invalid signature")
    except jwt.DecodeError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed, decode failed")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed, {e}")
    user_id = decoded.get('user_id')
    if decoded.get('type') != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication failed, invalid token type")
    if decoded.get('exp') < time.time():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed, token expired")

    user_obj = db.query(UserModel).filter(UserModel.id == user_id).first()
    return user_obj


def generate_access_token(user_id: int, expires_in: int = ACCESS_TOKEN_EXPIRY):
    now = time.time()
    payload = {
        'type': 'access',
        'user_id': user_id,
        'iat': int(now),
        'exp': int(now + expires_in)
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user_id: int, expires_in: int = REFRESH_TOKEN_EXPIRY):
    now = time.time()

    payload = {
        'type': 'refresh',
        'user_id': user_id,
        'iat': int(now),
        'exp': int(now + expires_in)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
