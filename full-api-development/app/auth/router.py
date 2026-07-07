from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select

from app import models, utils, oauth2, schemas
from app.database import SessionDep

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
async def login(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    result = await session.execute(select(models.User).where(models.User.email == user_credentials.username))
    user = result.scalar_one_or_none()
    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid Credentials."
        )
    access_token = oauth2.create_access_token(data={'user_id': user.id})
    return schemas.Token(access_token=access_token, token_type='bearer')
