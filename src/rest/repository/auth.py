from argon2.exceptions import VerifyMismatchError
from sqlalchemy import insert, select

from src.core.config import HASHER
from src.tables import Blacklist, User
from src.utils.db import DbRequest


async def get_active_user_by_id(user_id: int | str) -> User:
    """Получить пользователя по логину."""
    query = select(User).where(User.id == int(user_id), User.is_active)
    return await DbRequest.scalar(query)


async def ban_token(jti: str) -> None:
    """Заблокировать токен."""
    query = insert(Blacklist).values(jti=jti)
    await DbRequest.insert(query)


async def get_active_user_by_creds(
    email: str,
    password: str,
    admin: bool,
) -> User:
    """Получить пользователя по логину/паролю."""
    query = select(User).where(User.email == email, User.is_admin == admin)
    user = await DbRequest.scalar(query)
    if user is None:
        raise VerifyMismatchError()
    try:
        if not user.is_active:
            raise VerifyMismatchError()
        HASHER.verify(user.password, password)
    except VerifyMismatchError:
        raise VerifyMismatchError()
    return user
