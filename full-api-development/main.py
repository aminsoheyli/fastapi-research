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


@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    id = my_posts[-1]['id'] + 1
    post_dict = post.model_dump(exclude_unset=True) | {'id': id}
    my_posts.append(post_dict)
    return {"data": post_dict}


def find_post(post_id) -> dict | None:
    for post in my_posts:
        if post['id'] == post_id:
            return post
    return None


@app.get('/posts/latest')
def get_latest_post():
    if len(my_posts) == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": my_posts[-1]}


