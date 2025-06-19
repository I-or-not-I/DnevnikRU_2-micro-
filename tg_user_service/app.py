"""
Основной модуль запуска FastAPI сервера.
"""

from os import environ
from json import loads
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run

from routers import tg_bot
from utils.logger import Logger
from src.controller import AbstractController, Controller
from src.template_engine import AbstractTemplateEngine, TemplateEngine
from src.api import AbstractApi, Api
from src.markups import AbstractMarkups, Markups
from routers import abstract, base

from config import PARSER_IP, LOGGING_LEVEL, HOST, PORT, TIMEOUT, TEMPLATES_PATH


def main() -> None:
    """Основная функция инициализации и запуска сервера.

    Выполняет:
    1. Настройку системы логирования
    2. Создание FastAPI приложения
    3. Настройку CORS политик
    4. Инициализацию компонентов системы:
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

    template_engine: AbstractTemplateEngine = TemplateEngine(TEMPLATES_PATH)
    api: AbstractApi = Api(PARSER_IP, TIMEOUT)
    markups: AbstractMarkups = Markups()
    controller: AbstractController = Controller(api, template_engine, markups)

    routers: tuple[abstract.AbstractRouter, ...] = (base.Router(), tg_bot.Router(controller))
    for router in routers:
        app.include_router(router.get_router())

    run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
