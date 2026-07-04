from contextlib import asynccontextmanager
from typing import Annotated

import asyncpg
from fastapi import FastAPI, HTTPException, Request, Response, status, Depends
from pydantic import BaseModel

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_host,
        min_size=5,
        max_size=20,
    )
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


async def get_db(request: Request):
    async with request.app.state.pool.acquire() as conn:
        yield conn


DbConnection = Annotated[asyncpg.Connection, Depends(get_db)]


@app.get("/")
async def root():
    return {"data": "Welcome to my API!"}


@app.get('/posts')
async def get_posts(conn: DbConnection):
    posts = await conn.fetch('SELECT * FROM posts')
    return {"data": posts}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(post: Post, conn: DbConnection):
    new_post = await conn.fetchrow(
        'INSERT INTO posts (title, content, published) VALUES ($1, $2, $3) RETURNING *',
        post.title,
        post.content,
        post.published
    )

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
async def get_post(post_id: int, conn: DbConnection):
    post = await conn.fetchrow(
        'SELECT * FROM posts WHERE id = $1',
        post_id
    )
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
async def delete_post(post_id: int, conn: DbConnection):
    deleted_post = await conn.fetchrow(
        'DELETE FROM posts WHERE id = $1 RETURNING *',
        post_id
    )
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
