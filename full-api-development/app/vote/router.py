from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app import schemas, models
from app.database import SessionDep
from app.oauth2 import GetCurrentUserDep

router = APIRouter(prefix='/vote', tags=['Vote'])


@router.post('/')
async def login(vote: schemas.Vote, session: SessionDep, user: GetCurrentUserDep):
    post = await session.get(models.Post, vote.post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Post does not exist'
        )
    result = await session.execute(
        select(models.Vote).where(models.Vote.post_id == vote.post_id, models.Vote.user_id == user.id)
    )
    found_vote = result.scalars().first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'You have already voted on post {vote.post_id}'
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=user.id)
        session.add(new_vote)
        await session.commit()
        return {'message': 'successfully added vote'}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Vote does not exist'
            )
        await session.delete(found_vote)
        await session.commit()
        return {'message': 'successfully deleted vote'}
