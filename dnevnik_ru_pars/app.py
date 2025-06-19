"""
Основной модуль запуска FastAPI сервера.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from utils.logger import Logger
from routers import abstract, base, dnevnik
from src.async_parser import AbstractParser, Parser
from config import LOGGING_LEVEL, HOST, PORT, TIMEOUT


def main() -> None:
    """Основная функция инициализации и запуска сервера.

    Выполняет:
    1. Настройку системы логирования
    2. Создание FastAPI приложения
    3. Добавление CORS middleware
    4. Инициализацию парсера данных
    5. Подключение роутеров
    6. Запуск сервера через Uvicorn

    :raises Exception: При ошибках инициализации компонентов
    """
    Logger(LOGGING_LEVEL)

    app: FastAPI = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    parser: AbstractParser = Parser(TIMEOUT)

    routers: tuple[abstract.AbstractRouter, ...] = (base.Router(), dnevnik.Router(parser))
    for router in routers:
        app.include_router(router.get_router())

    run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
