from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine, Base
from .post.router import router as post_router
from .user.router import router as user_router
from .auth import router as auth_router


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    await init_models()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(post_router)
app.include_router(user_router)
app.include_router(auth_router)
