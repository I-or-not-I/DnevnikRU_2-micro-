"""
Конкретная реализация роутера для проверки работоспособности сервиса.
"""

from fastapi import APIRouter
from routers.abstract import AbstractRouter


class Router(AbstractRouter):
    """Реализация абстрактного роутера с базовым функционалом.

    Наследует:
    - :class:`AbstractRouter`

    .. note::
        Автоматически регистрирует:
        - GET / (проверка работоспособности сервиса)
    """

    def __init__(self) -> None:
        """Инициализация роутера и регистрация эндпоинтов."""
        self.__router: APIRouter = APIRouter()
        self.__routs_register()

    def __routs_register(self) -> None:
        """Приватный метод регистрации маршрутов.

        :meta private:
        """
        self.__router.add_api_route("/", self.__ping, methods=["GET"])

    async def __ping(self) -> str:
        """Эндпоинт проверки работоспособности сервиса.

        :return: Ответ "PONG" в виде строки
        :rtype: str
        """
        return "PONG"

    def get_router(self) -> APIRouter:
        """Получение сконфигурированного роутера.

        :return: Экземпляр APIRouter с зарегистрированными маршрутами
        :rtype: :class:`APIRouter`
        """
        return self.__router

    def get_endpoints(self) -> tuple:
        """Получение всех эндпоинтов

        :return: список всех эндпоинтов
        :rtype: tuple
        """

        return ("/",)
