from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select

from app import models, utils, oauth2
from app.database import SessionDep

router = APIRouter(tags=['Authentication'])


@router.post('/login')
async def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    result = await session.execute(select(models.User).where(models.User.email == user_credentials.username))
    user = result.scalar_one_or_none()
    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid Credentials."
        )
    access_token = oauth2.create_access_token(data={'user_id': user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}
