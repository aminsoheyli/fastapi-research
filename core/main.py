from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from core.database import get_db

security = HTTPBasic()

from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasic

from core.tasks.routes import router as tasks_routes
from core.users.models import UserModel
from core.users.routes import router as users_routes

tags_metadata = [
    {
        "name": "tasks",
        "description": "Operations related to task management",
        "externalDocs": {
            "description": "More about tasks",
            "url": "https://example.com/docs/tasks"
        }
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    yield
    print("Application shutdown")


app = FastAPI(
    title="Todo Application",
    description=(
        "A simple and efficient Todo management API built with FastAPI. "
        "This API allows users to create, retrieve, update, and delete tasks. "
        "It is designed for task tracking and productivity improvement."
    ),
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Ali Bigdeli",
        "url": "https://thealibigdeli.ir",
        "email": "bigdeli.ali3@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }, lifespan=lifespan, openapi_tags=tags_metadata)

app.include_router(tasks_routes)
app.include_router(users_routes)


def get_authenticated_user(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)],
        db: Annotated[Session, Depends(get_db)]
):
    user = db.query(UserModel).filter(UserModel.username == credentials.username).first()
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


security = HTTPBasic()


@app.get('/public')
def public_route():
    return {"message": "This is a public route"}


@app.get('/private')
def private_route(user: Annotated[UserModel, Depends(get_authenticated_user)]):
    print(user.username)
    return {"message": "This is a private route"}
