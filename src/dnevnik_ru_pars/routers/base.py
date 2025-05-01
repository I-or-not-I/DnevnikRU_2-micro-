"""
Модуль с конкретной реализацией роутера FastAPI.
"""

from fastapi import APIRouter
from routers.abstract import AbstractRouter


class Router(AbstractRouter):
    """Конкретная реализация роутера FastAPI.

    Наследует:
    - :class:`AbstractRouter`

    .. note::
        Автоматически регистрирует эндпоинты при инициализации
    """

    def __init__(self) -> None:
        """Инициализация роутера и регистрация эндпоинтов."""
        self.__router: APIRouter = APIRouter()
        self.__routs_register()

    def __routs_register(self) -> None:
        """Приватный метод для регистрации маршрутов.

        :meta private:
        """
        self.__router.add_api_route("/", self.__ping, methods=["GET"])

    async def __ping(self) -> str:
        """Эндпоинт для проверки работоспособности сервиса.

        :return: Строка "PONG"
        :rtype: str

        .. note::
            Доступен по GET-запросу на корневой URL
        """
        return "PONG"

    def get_router(self) -> APIRouter:
        """Получение сконфигурированного роутера.

        :return: Экземпляр APIRouter с зарегистрированными маршрутами
        :rtype: :class:`APIRouter`
        """
        return self.__router
