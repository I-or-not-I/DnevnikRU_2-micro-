"""
Асинхронный модуль роутера для обработки сообщений Telegram через FastAPI.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from routers.abstract import AbstractRouter
from src.async_controller import AbstractController
from models.message import Message


class Router(AbstractRouter):
    """Асинхронная реализация роутера для Telegram-сообщений."""

    def __init__(self, controller: AbstractController) -> None:
        self.__controller: AbstractController = controller
        self.__router: APIRouter = APIRouter()

        self.__handlers: dict = {
            "start": self.__start,
            "text_messages": self.__text_messages,
            "help": self.__help,
            "change_create_data": self.__change_create_data,
            "show_data": self.__show_data,
            "show_marks": self.__show_marks,
            "show_timetable": self.__show_timetable,
        }

        self.__register_routes()

    def __register_routes(self) -> None:
        """Регистрация асинхронных эндпоинтов."""
        for path, handler in self.__handlers.items():
            self.__router.add_api_route(f"/{path}", handler, methods=["POST"], response_model=Message)

    async def __start(self, message: Message) -> JSONResponse:
        """Асинхронный обработчик команды /start."""
        content: dict = await self.__controller.start(message)
        return JSONResponse(content=content)

    async def __text_messages(self, message: Message) -> JSONResponse:
        """Асинхронный обработчик текстовых сообщений."""
        content: dict = await self.__controller.text_messages(message)
        return JSONResponse(content=content)

    async def __help(self, message: Message) -> JSONResponse:
        """Асинхронный обработчик команды /help."""
        content: dict = await self.__controller.help(message)
        return JSONResponse(content=content)

    async def __change_create_data(self, message: Message) -> JSONResponse:
        """Асинхронный обработчик изменения данных."""
        content: dict = await self.__controller.change_create_data(message)
        return JSONResponse(content=content)

    async def __show_data(self, message: Message) -> JSONResponse:
        """Асинхронный обработчик показа данных."""
        content: dict = await self.__controller.show_data(message)
        return JSONResponse(content=content)

    async def __show_marks(self, message: Message) -> JSONResponse:
        """Асинхронный обработчик показа оценок."""
        content: dict = await self.__controller.show_marks(message)
        return JSONResponse(content=content)

    async def __show_timetable(self, message: Message) -> JSONResponse:
        """Асинхронный обработчик показа расписания."""
        content: dict = await self.__controller.show_timetable(message)
        return JSONResponse(content=content)

    def get_router(self) -> APIRouter:
        """Получение сконфигурированного роутера."""
        return self.__router

    def get_endpoints(self) -> tuple:
        """Получение всех эндпоинтов

        :return: список всех эндпоинтов
        :rtype: tuple
        """
        return tuple(self.__handlers.keys())
