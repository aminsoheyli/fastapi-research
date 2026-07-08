from fastapi import HTTPException, Response, status, APIRouter
from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload, selectinload

from .. import models, schemas
from ..database import SessionDep
from ..oauth2 import GetCurrentUserDep

router = APIRouter(prefix='/posts', tags=['Posts'])


@router.get('/', response_model=list[schemas.PostResponse])
async def get_posts(session: SessionDep, user: GetCurrentUserDep, limit: int = 10, skip: int = 0, search: str = ''):
    results = await session.execute(
        select(models.Post, func.count(models.Vote.user_id).label('votes'))
        .join(models.Vote, onclause=models.Post.id == models.Vote.post_id, isouter=True)
        .options(selectinload(models.Post.owner))
        .where(models.Post.title.contains(search))
        .order_by(models.Post.created_at.desc())
        .limit(limit)
        .offset(skip)
        .group_by(models.Post.id)
    )
    posts = [{"post": row.Post, "votes": row.votes} for row in results.all()]
    return posts


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, session: SessionDep, user: GetCurrentUserDep):
    new_post = models.Post(**post.model_dump(), user_id=user.id)
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post


@router.get('/latest', response_model=schemas.PostResponse)
async def get_latest_post(session: SessionDep, user: GetCurrentUserDep):
    result = await session.execute(
        select(models.Post, func.count(models.Vote.user_id).label('votes'))
        .join(models.Vote, onclause=models.Post.id == models.Vote.post_id, isouter=True)
        .order_by(models.Post.created_at.desc())
        .options(selectinload(models.Post.owner))
        .group_by(models.Post.id)
        .limit(1)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"post": row.Post, "votes": row.votes}


@router.get('/{post_id}', response_model=schemas.PostResponse)
async def get_post(post_id: int, session: SessionDep, user: GetCurrentUserDep):
    result = await session.execute(
        select(models.Post, func.count(models.Vote.user_id).label('votes'))
        .join(models.Vote, onclause=models.Post.id == models.Vote.post_id, isouter=True)
        .where(models.Post.id == post_id)
        .options(selectinload(models.Post.owner))
        .group_by(models.Post.id)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    return {"post": row.Post, "votes": row.votes}


@router.put('/{post_id}', response_model=schemas.Post)
async def update_post(post_id: int, post_update: schemas.PostCreate, session: SessionDep, user: GetCurrentUserDep):
    update_data = post_update.model_dump()
    if not update_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No fields provided to update")
    result = await session.execute(
        update(models.Post).where(models.Post.id == post_id).values(**update_data).returning(models.Post))
    updated_post = result.scalar_one_or_none()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    await session.commit()
    return updated_post


@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, session: SessionDep, user: GetCurrentUserDep):
    post = await session.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")

    await session.delete(post)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
