"""Модуль запуска приложения для дебага."""
from os import getenv
from typing import Dict

import uvicorn


def listen_url_to_config(listen: str) -> Dict:  # noqa  WPS210
    """Получение конфига для дебага приложения."""
    web_params = {}
    input_val = listen

    if not input_val:
        input_val = ""

    schema: str = input_val[:4]
    listen_value: str = input_val[7:]

    if schema == "http":
        host, port = listen_value.split(":")

        if not port:
            port = 8080

        web_params = {"host": host, "port": int(port)}

    return web_params if web_params else {"host": "0.0.0.0", "port": 8080}


def main() -> None:
    """Запуск приложения."""
    params = listen_url_to_config(getenv("PROJECT_HOST"))
    params["reload"] = True

    uvicorn.run("src.app:application", **params)


if __name__ == "__main__":
    main()
