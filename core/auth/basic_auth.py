from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from core.database import get_db
from core.users.models import UserModel

security = HTTPBasic()


def get_authenticated_user(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        db: Annotated[Session, Depends(get_db)]
):
    user = db.query(UserModel).filter(UserModel.username == credentials.username).first()
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user
