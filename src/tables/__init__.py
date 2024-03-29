"""Пакет с таблицами."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()

from src.tables.token import *  # noqa F401
from src.tables.user import *  # noqa F401
from src.tables.storehouse import *  # noqa F401
from src.tables.immovable import *  # noqa F401
from src.tables.item import *  # noqa F401
from src.tables.medicine import *  # noqa F401
