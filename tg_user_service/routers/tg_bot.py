"""
Асинхронный модуль роутера для обработки сообщений Telegram через FastAPI.

Предоставляет API-эндпоинты для обработки команд Telegram:
- /start - приветствие
- /help - помощь
- /change_create_data - изменение данных
- /show_data - просмотр данных
- /show_marks - просмотр оценок
- /show_timetable - просмотр расписания

Основные компоненты:
    Router: Класс роутера, регистрирующий эндпоинты и делегирующий обработку контроллеру.

Зависимости:
    AbstractRouter: Абстрактный базовый класс для роутеров
    AbstractController: Абстракция для бизнес-логики
    Message: Модель сообщения Telegram

.. note::
    Все эндпоинты принимают данные в формате Message через POST-запросы.
    Ответы возвращаются в формате JSON, совместимом с Telegram API.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from routers.abstract import AbstractRouter
from src.controller import AbstractController
from models.message import Message


class Router(AbstractRouter):
    """
    Реализация роутера для обработки команд Telegram.

    :param controller: Экземпляр контроллера для обработки бизнес-логики
    :type controller: AbstractController
    :returns: Инициализированный экземпляр роутера
    :rtype: Router
    """

    def __init__(self, controller: AbstractController) -> None:
        self.__controller: AbstractController = controller
        self.__router: APIRouter = APIRouter()

        self.__handlers: dict = {
            "start": self.__start,
            "help": self.__help,
            "change_create_data": self.__change_create_data,
            "show_data": self.__show_data,
            "show_marks": self.__show_marks,
            "show_timetable": self.__show_timetable,
        }

        self.__register_routes()

    def __register_routes(self) -> None:
        """Приватный метод регистрации маршрутов для команд.

        :meta private:
        """
        for path, handler in self.__handlers.items():
            self.__router.add_api_route(f"/{path}", handler, methods=["POST"], response_model=Message)

    async def __start(self, message: Message) -> JSONResponse:
        """
        Асинхронный обработчик команды /start.

        :param message: Входящее сообщение Telegram
        :type message: Message
        :returns: Ответ для Telegram API в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        content: dict = await self.__controller.start(message)
        return JSONResponse(content=content)

    async def __help(self, message: Message) -> JSONResponse:
        """
        Асинхронный обработчик команды /help.

        :param message: Входящее сообщение Telegram
        :type message: Message
        :returns: Ответ для Telegram API в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        content: dict = await self.__controller.help(message)
        return JSONResponse(content=content)

    async def __change_create_data(self, message: Message) -> JSONResponse:
        """
        Асинхронный обработчик изменения или создания данных пользователя.

        :param message: Входящее сообщение Telegram
        :type message: Message
        :returns: Ответ для Telegram API в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        content: dict = await self.__controller.change_create_data(message)
        return JSONResponse(content=content)

    async def __show_data(self, message: Message) -> JSONResponse:
        """
        Асинхронный обработчик показа данных пользователя.

        :param message: Входящее сообщение Telegram
        :type message: Message
        :returns: Ответ для Telegram API в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        content: dict = await self.__controller.show_data(message)
        return JSONResponse(content=content)

    async def __show_marks(self, message: Message) -> JSONResponse:
        """
        Асинхронный обработчик показа оценок пользователя.

        :param message: Входящее сообщение Telegram
        :type message: Message
        :returns: Ответ для Telegram API в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        content: dict = await self.__controller.show_marks(message)
        return JSONResponse(content=content)

    async def __show_timetable(self, message: Message) -> JSONResponse:
        """
        Асинхронный обработчик показа расписания занятий.

        :param message: Входящее сообщение Telegram
        :type message: Message
        :returns: Ответ для Telegram API в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        content: dict = await self.__controller.show_timetable(message)
        return JSONResponse(content=content)

    def get_router(self) -> APIRouter:
        """
        Получение сконфигурированного роутера.

        :return: Готовый к использованию APIRouter
        :rtype: :class:`APIRouter`
        """
        return self.__router

    def get_endpoints(self) -> tuple:
        """
        Получение списка всех доступных эндпоинтов.

        :return: Кортеж с именами эндпоинтов (команд)
        :rtype: tuple
        """
        return tuple(self.__handlers.keys())
