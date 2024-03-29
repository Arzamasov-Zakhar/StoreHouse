"""Модуль для генерации токенов."""

import secrets
from datetime import datetime, timedelta
from hashlib import sha256 as _sha256
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

import jwt as pyjwt
from authlib.jose import jwt
from fastapi import FastAPI, Request
from sqlalchemy import select

from src.core.config import settings
from src.tables.token import Blacklist
from src.tables.user import User
from src.utils.common import EXPIRE_FORMAT
from src.utils.db import DbRequest
from src.utils.exceptions.jwt import BlacklistedError

HEADER = {"alg": "HS256"}
AUTH_HEADER = "Authorization"


def build_key(value: str, secret_key: str) -> str:
    """Build key for jwt token."""
    return "??".join([value, secret_key])


def create_token(
    payload: dict = None,
    expires: datetime = None,
    access_jti: Optional[str] = None,
) -> Tuple[str, str]:
    """Generate JWT token."""
    if not payload:
        payload = {}

    if not expires:
        expires = datetime.utcnow() + timedelta(hours=24)

    payload = {"exp": int(expires.timestamp()), "jti": uuid4().hex, **payload}
    if access_jti:
        payload["access_jti"] = access_jti

    token = jwt.encode(HEADER, payload, settings.JWT_KEY)

    return token.decode("ASCII"), payload["jti"]


async def check_token_blacklist(app: FastAPI, jti: str):  # noqa: ANN20
    """Check if token in blacklist."""
    query = select(Blacklist).where(Blacklist.jti == jti)
    return await DbRequest.scalar(query)


def read_token(request: Any, type_: str) -> str:
    """Read token of given type from request 'Authorization' header."""
    auth_header: str = request.headers.get(AUTH_HEADER)
    assert bool(auth_header), "Header is not provided"
    assert (
        auth_header.split()[0].upper() == type_.upper()
    ), "Invalid token type"
    return auth_header.split()[1]  # noqa R504


async def read_jwt_token(
    request: Request, key: str = "", token: str = None
) -> dict:
    """
    Read access token from request header.

    (If key presents, validates signature with it)
    """
    auth_header: str = request.headers.get(AUTH_HEADER)

    token = token or read_token(request, "JWT")
    payload = jwt_decode(token, key=key, verify=bool(key))

    if payload["exp"] < datetime.utcnow():
        raise PermissionError
    if await check_token_blacklist(request.app, payload["jti"]):
        raise BlacklistedError
    if not any((auth_header, payload)):
        return payload

    return {**payload, "token": token}


def create_reset_token() -> Tuple[str, datetime]:
    """Create reset token."""
    reset_token = secrets.token_urlsafe(nbytes=100)

    expiry = datetime.utcnow() + timedelta(seconds=settings.RESET_LIFETIME)

    return reset_token, expiry


def sha256(str_: str, salt: str) -> str:
    """Hash string with sha256 hashing algorithm."""
    return _sha256(build_key(str_, salt).encode("utf-8")).hexdigest()


def prepare_token_from_app(token: str) -> str:
    """Handle token preparation before writing to db or query."""
    return sha256(token, settings.secret_key)


def prepare_token(info: Any, token: str) -> str:
    """
    Do the same as prepare_token_from_app.

    (handles process via info var.)
    """
    return prepare_token_from_app(token)


def create_auth_token(
    auth_user: User,
    lifetime: Optional[timedelta] = None,
    access_jti: Optional[str] = None,
    return_jti: bool = False,
) -> Union[tuple[str, str], str]:
    """Create auth token with given username and signature key."""
    if not lifetime and not access_jti:
        lifetime = timedelta(seconds=settings.ACCESS_LIFETIME)
    elif not lifetime and access_jti:
        lifetime = timedelta(seconds=settings.REFRESH_LIFETIME)
    expires = datetime.utcnow() + lifetime

    payload = {
        "id": auth_user.id,
        "iss": "imin",  # TODO: Заменить
    }

    token, jti = create_token(payload, expires, access_jti)
    if return_jti:
        return token, jti
    return token


def create_token_pair(active_user: User) -> Tuple[str, str]:
    """Создать пару токенов."""
    access_token, jti = create_auth_token(active_user, return_jti=True)
    refresh_token = create_auth_token(active_user, access_jti=jti)

    return access_token, refresh_token


def jwt_decode(
    jwt: str,
    key: str = "",
    verify: bool = True,
    algorithms: Optional[List[str]] = None,
    options: Optional[dict] = None,
    **kwargs: Dict,
) -> dict:
    """Get payload from token with formated expires key."""
    algorithms = "HS256"
    payload = pyjwt.decode(jwt, key, algorithms, options, verify, **kwargs)
    if payload.get("exp"):
        payload["exp"] = datetime.fromtimestamp(payload.get("exp"))

    if payload.get("expires"):
        payload["exp"] = datetime.strptime(
            payload.get("expires"), EXPIRE_FORMAT
        )

    return payload
