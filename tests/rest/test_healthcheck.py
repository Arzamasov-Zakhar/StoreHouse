"""Модуль с тестами для healthcheck запросов."""
import pytest
from starlette import status as status_code
from starlette.testclient import TestClient


@pytest.mark.asyncio
async def test_backend(test_client: TestClient) -> None:
    """Тест для проверки healthcheck ручки."""
    response = test_client.get(
        test_client.app.url_path_for("healthcheck_backend"),
    )
    assert response.status_code == status_code.HTTP_200_OK


@pytest.mark.asyncio
async def test_database(test_client: TestClient) -> None:
    """Тест для проверки healthcheck ручки."""
    response = test_client.get(
        test_client.app.url_path_for("healthcheck_database"),
    )
    assert response.status_code == status_code.HTTP_200_OK
