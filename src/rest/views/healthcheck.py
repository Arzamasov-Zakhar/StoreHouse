"""Модуль с тестовой view."""
from fastapi import APIRouter
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

from src.core.db import async_session

router = APIRouter()


@router.get("/")
async def healthcheck_backend() -> str:
    """Урл для проверки бэка."""
    return "OK"


@router.get("/db")
async def healthcheck_database() -> str:
    """Урл для проверки базы данных."""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        return "OK"
    except OperationalError:
        return "database is not responding"
