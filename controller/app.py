"""
Основной модуль запуска FastAPI сервера для образовательного бота.
"""

from os import environ
from json import loads
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from utils.logger import Logger
from src.async_controller import AbstractController, Controller
from src.async_db import AbstractDb, Database
from src.template_engine import AbstractTemplateEngine, TemplateEngine
from src.async_api import AbstractApi, Api
from src.markups import AbstractMarkups, Markups
from routers import abstract, base, async_bot

from config import PARSER_IP, LOGGING_LEVEL


def main() -> None:
    """Основная функция инициализации и запуска сервера.

    Выполняет:
    1. Настройку системы логирования
    2. Создание FastAPI приложения
    3. Настройку CORS политик
    4. Инициализацию компонентов системы:
       - База данных
       - Шаблонизатор
       - API клиент
       - Генератор разметок
       - Бизнес-логика
    5. Подключение роутеров
    6. Запуск сервера

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

    DB_DATA = loads(environ.get("DB_DATA"))
    db: AbstractDb = Database(DB_DATA)
    template_engine: AbstractTemplateEngine = TemplateEngine("templates")
    api: AbstractApi = Api(PARSER_IP)
    markups: AbstractMarkups = Markups()
    controller: AbstractController = Controller(api, db, template_engine, markups)

    routers: tuple[abstract.AbstractRouter] = (base.Router(), async_bot.Router(controller))
    for router in routers:
        app.include_router(router.get_router())

    run(app, host="0.0.0.0", port=8019)


if __name__ == "__main__":
    main()
