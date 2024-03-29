"""Модуль с утилитами."""
from os import getenv


def get_database_url(sync: bool = True) -> str:
    """Получить ссылку на базу."""
    user = getenv("DB_USER", "postgres")
    name = getenv("DB_NAME")
    password = getenv("DB_PASS")
    host = getenv("DB_HOST")
    port = getenv("DB_PORT")
    driver = "" if sync else "+asyncpg"

    return f"postgresql{driver}://{user}:{password}@{host}:{port}/{name}"


EXPIRE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
