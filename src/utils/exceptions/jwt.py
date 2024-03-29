"""Модуль с jwt исключениями."""


class BlacklistedError(Exception):
    """Ошибка токена в черном списке."""


class TokenGoneOffError(Exception):
    """Истек срок действия токена."""
