"""Модуль с инструментами для тестов."""
import os
from contextlib import contextmanager, suppress

from sqlalchemy_utils import create_database, drop_database
from sqlalchemy_utils.functions import database_exists
from yarl import URL


@contextmanager
def get_tmp_database(**kwargs: dict) -> str:
    """Создать временную бд для тестов."""
    tmp_db_url = os.getenv("WRITE_DB")
    if kwargs.get("template"):
        db_url = URL(tmp_db_url).path.replace("_template", "_test")
    else:
        db_url = URL(tmp_db_url).path.replace("_test", "_template")

    tmp_db_url = str(URL(tmp_db_url).with_path(db_url)) + str(
        os.getenv("PYTEST_XDIST_WORKER", "")
    )

    if tmp_db_url and database_exists(tmp_db_url):
        drop_database(tmp_db_url)
    create_database(tmp_db_url, **kwargs)
    with suppress(Exception):
        yield tmp_db_url
    with suppress(Exception):
        drop_database(tmp_db_url)
