"""
Модуль роутера для обработки сообщений Telegram через FastAPI.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Callable
from routers.abstract import AbstractRouter
from src.controller import AbstractController
from models.message import Message


class Router(AbstractRouter):
    """Конкретная реализация роутера для обработки Telegram-сообщений.

    Наследует:
    - :class:`AbstractRouter`

    :param controller: Контроллер для обработки бизнес-логики
    :type controller: :class:`AbstractController`

    .. note::
        Регистрирует следующие эндпоинты (POST):
        - /start
        - /text_messages
        - /help
        - /change_create_data
        - /show_data
        - /show_marks
    """

    def __init__(self, controller: AbstractController) -> None:
        self.__controller: AbstractController = controller
        self.__router: APIRouter = APIRouter()
        self.__routs_register()

    def __routs_register(self) -> None:
        """Приватный метод регистрации базовых маршрутов.

        :meta private:
        """
        base_register: dict = {
            "start": self.__start,
            "text_messages": self.__text_messages,
            "help": self.__help,
            "change_create_data": self.__change_create_data,
            "show_data": self.__show_data,
            "show_marks": self.__show_marks,
        }
        for path in base_register.keys():
            self.__base_register(path, base_register[path])

    def __base_register(self, path: str, endpoint: Callable) -> None:
        """Базовый регистратор эндпоинтов.

        :param path: URL путь
        :param endpoint: Обработчик запроса
        :type path: str
        :type endpoint: Callable
        :meta private:
        """
        self.__router.add_api_route(f"/{path}", endpoint, methods=["POST"], response_model=Message)

    async def __start(self, message: Message) -> JSONResponse:
        """Обработчик команды /start.

        :param message: Входящее сообщение
        :type message: :class:`Message`
        :return: Ответ контроллера
        :rtype: :class:`JSONResponse`
        """
        content: dict = self.__controller.start(message)
        return JSONResponse(content=content)

    async def __text_messages(self, message: Message) -> JSONResponse:
        """Обработчик текстовых сообщений.

        :param message: Входящее сообщение
        :type message: :class:`Message`
        :return: Ответ контроллера
        :rtype: :class:`JSONResponse`
        """
        content: dict = self.__controller.text_messages(message)
        return JSONResponse(content=content)

    async def __help(self, message: Message) -> JSONResponse:
        """Обработчик команды /help.

        :param message: Входящее сообщение
        :type message: :class:`Message`
        :return: Ответ контроллера
        :rtype: :class:`JSONResponse`
        """
        content: dict = self.__controller.help(message)
        return JSONResponse(content=content)

    async def __change_create_data(self, message: Message) -> JSONResponse:
        """Обработчик изменения данных.

        :param message: Входящее сообщение
        :type message: :class:`Message`
        :return: Ответ контроллера
        :rtype: :class:`JSONResponse`
        """
        content: dict = self.__controller.change_create_data(message)
        return JSONResponse(content=content)

    async def __show_data(self, message: Message) -> JSONResponse:
        """Обработчик показа данных.

        :param message: Входящее сообщение
        :type message: :class:`Message`
        :return: Ответ контроллера
        :rtype: :class:`JSONResponse`
        """
        content: dict = self.__controller.show_data(message)
        return JSONResponse(content=content)

    async def __show_marks(self, message: Message) -> JSONResponse:
        """Обработчик показа оценок.

        :param message: Входящее сообщение
        :type message: :class:`Message`
        :return: Ответ контроллера
        :rtype: :class:`JSONResponse`
        """
        content: dict = self.__controller.show_marks(message)
        return JSONResponse(content=content)

    def get_router(self) -> APIRouter:
        """Получение сконфигурированного роутера.

        :return: Экземпляр APIRouter с эндпоинтами
        :rtype: :class:`APIRouter`
        """
        return self.__router
