from typing import Annotated

from fastapi import Depends
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.users.models import TokenModel

security = HTTPBearer(scheme_name="Token")


def get_token_authenticated_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        db: Annotated[Session, Depends(get_db)]
):
    token_obj = db.query(TokenModel).filter_by(token=credentials.credentials).one_or_none()
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, invalid credentials",
        )
    return token_obj.user
