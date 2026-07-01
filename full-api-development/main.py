from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: int | None = None


my_posts = [
    Post(title='title of post 1', content='content of post 1').model_dump(exclude_unset=True) | {'id': 1},
    Post(title='favorite foods', content='I like pizza').model_dump(exclude_unset=True) | {'id': 2},
]


@app.get("/")
async def root():
    return {"data": "Welcome to my API!"}


@app.get('/posts')
def get_posts():
    return {"data": my_posts}
