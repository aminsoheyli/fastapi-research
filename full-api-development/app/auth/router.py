from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app import schemas, models, utils
from app.database import SessionDep

router = APIRouter(tags=['Authentication'])


@router.post('/login')
async def login(user_credentials: schemas.UserLogin, session: SessionDep):
    result = await session.execute(select(models.User).where(models.User.email == user_credentials.email))
    user = result.scalar_one_or_none()
    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invalid Credentials."
        )

    return 'token'
