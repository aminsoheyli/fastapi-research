from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Response, status, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from .database import engine, get_session, Base


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    await init_models()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get('/posts', response_model=list[schemas.Post])
async def get_posts(session: SessionDep):
    results = await session.execute(select(models.Post))
    posts = results.scalars().all()
    return posts


@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, session: SessionDep):
    new_post = models.Post(**post.model_dump())
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post


@app.get('/posts/latest', response_model=schemas.Post)
async def get_latest_post(session: SessionDep):
    query = select(models.Post).order_by(models.Post.created_at.desc()).limit(1)
    result = await session.execute(query)
    latest_post = result.scalar_one_or_none()
    if latest_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return latest_post


@app.get('/posts/{post_id}', response_model=schemas.Post)
async def get_post(post_id: int, session: SessionDep):
    result = await session.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    return post


@app.put('/posts/{post_id}', response_model=schemas.Post)
async def update_post(post_id: int, post_update: schemas.PostCreate, session: SessionDep):
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


@app.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, session: SessionDep):
    post = await session.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    await session.delete(post)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
