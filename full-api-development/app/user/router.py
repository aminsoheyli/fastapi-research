from fastapi import HTTPException, status, APIRouter
from sqlalchemy import select

from .. import models, schemas, utils
from ..database import SessionDep

router = APIRouter()


@router.post('/users', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, session: SessionDep):
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.get('/users/{user_id}', response_model=schemas.UserResponse)
async def get_user(user_id: int, session: SessionDep):
    result = await session.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
    return user
