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


@app.get('/posts/{post_id}')
def get_post(post_id: int):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    return {"data": post}


@app.put('/posts/{post_id}')
def update_post(post_id: int, post_update: Post):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    update_data = post_update.model_dump()
    post.update(update_data)
    return {"data": update_data}


@app.delete('/posts/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    post = find_post(post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {post_id} not found")
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
