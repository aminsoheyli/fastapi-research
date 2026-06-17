import datetime

import jwt
from fastapi.security import HTTPBearer

from core.config import settings

security = HTTPBearer(scheme_name="Token")

ACCESS_TOKEN_EXPIRY = int(datetime.timedelta(minutes=5).total_seconds())
REFRESH_TOKEN_EXPIRY = int(datetime.timedelta(days=1).total_seconds())


def generate_access_token(user_id: int, expires_in: int = ACCESS_TOKEN_EXPIRY):
    now = datetime.datetime.now()
    payload = {
        'type': 'access',
        'user_id': user_id,
        'iat': now,
        'exp': now + datetime.timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')


def generate_refresh_token(user_id: int, expires_in: int = REFRESH_TOKEN_EXPIRY):
    now = datetime.datetime.now()
    payload = {
        'type': 'refresh',
        'user_id': user_id,
        'iat': now,
        'exp': now + datetime.timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
