from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .auth.router import router as auth_router
from .database import engine
from .post.router import router as post_router
from .user.router import router as user_router
from .vote.router import router as vote_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(post_router)
app.include_router(user_router)
app.include_router(vote_router)
app.include_router(auth_router)
