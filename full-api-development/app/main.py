from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
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


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/")
async def root():
    return {"data": "Welcome to my API!"}


@app.get('/posts')
async def get_posts(session: SessionDep):
    results = await session.execute(select(models.Post))
    posts = results.scalars().all()
    return {"data": posts}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, session: SessionDep):
    new_post = models.Post(**post.model_dump())
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return {"data": new_post}


@app.get('/posts/latest')
async def get_latest_post(conn: DbConnection):
    latest_post = await conn.fetchrow(
        'SELECT * FROM posts ORDER BY created_at DESC LIMIT 1',
    )
    if latest_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": latest_post}


@app.get('/posts/{post_id}')
async def get_post(post_id: int, session: SessionDep):
    result = await session.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    return {"data": post}


@app.put('/posts/{post_id}')
async def update_post(post_id: int, post_update: Post, conn: DbConnection):
    updated_post = await conn.fetchrow(
        'UPDATE posts SET title = $1,content = $2,published = $3 WHERE id = $4 RETURNING *',
        post_update.title,
        post_update.content,
        post_update.published,
        post_id
    )
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    return {"data": updated_post}


@app.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, session: SessionDep):
    post = await session.get(models.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    await session.delete(post)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
