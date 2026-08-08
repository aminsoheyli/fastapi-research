import asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..database import engine

router = APIRouter(tags=["Health"])


@router.get("/healthz")
async def healthz():
    try:
        async with asyncio.timeout(2):
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
    except (SQLAlchemyError, TimeoutError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "unavailable"},
        )

    return {"status": "healthy", "database": "available"}
