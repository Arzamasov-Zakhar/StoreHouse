from sqlalchemy import insert, select

from src.tables import User
from src.utils.db import DbRequest


async def get_existing_user(email: str) -> User:
    """Проверить существует ли пользователь с таким email."""
    query = select(User).where(User.email == email)
    return await DbRequest.scalar(query)


async def create_user(email: str, password: str) -> int:
    """Создать пользователя."""
    query = (
        insert(User)
        .values(email=email, password=password, is_active=True)
        .returning(User.id)
    )
    return (await DbRequest.insert(query)).scalar()
