"""Модуль с исключениями repository."""


class NotFoundException(Exception):
    """Исключение 'Запись не найдена'."""


class AlreadExistsException(Exception):
    """Исключение 'Запись уже существует'."""


class DeniedRepositoryException(Exception):
    """Исключение 'Доступ в репозетории был запрещен'."""


class RegistrationException(Exception):
    """Исключение 'Ошибка регистрации'."""
