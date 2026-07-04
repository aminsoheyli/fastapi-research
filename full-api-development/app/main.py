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


my_posts = [
    Post(title='title of post 1', content='content of post 1').model_dump(exclude_unset=True) | {'id': 1},
    Post(title='favorite foods', content='I like pizza').model_dump(exclude_unset=True) | {'id': 2},
]


async def get_db(request: Request):
    async with request.app.state.pool.acquire() as conn:
        yield conn


DbConnection = Annotated[asyncpg.Connection, Depends(get_db)]


@app.get("/")
async def root():
    return {"data": "Welcome to my API!"}


@app.get('/posts')
async def get_posts():
    return {"data": my_posts}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    id = my_posts[-1]['id'] + 1
    post_dict = post.model_dump(exclude_unset=True) | {'id': id}
    my_posts.append(post_dict)
    return {"data": post_dict}


async def find_post(post_id) -> dict | None:
    for post in my_posts:
        if post['id'] == post_id:
            return post
    return None


@app.get('/posts/latest')
async def get_latest_post():
    if len(my_posts) == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": my_posts[-1]}


@app.get('/posts/{post_id}')
async def get_post(post_id: int):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    return {"data": post}


@app.put('/posts/{post_id}')
async def update_post(post_id: int, post_update: Post):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    update_data = post_update.model_dump()
    post.update(update_data)
    return {"data": update_data}


@app.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get('/db')
async def get_db(conn: DbConnection):
    values = await conn.fetch('SELECT * FROM posts')
    print(f'db values: {values}')
    await conn.close()
