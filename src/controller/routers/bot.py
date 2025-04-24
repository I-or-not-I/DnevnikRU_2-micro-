from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Callable

from routers.abstract import AbstractRouter
from src.controller import AbstractController
from models.message import Message


class Router(AbstractRouter):
    def __init__(self, controller: AbstractController) -> None:
        self.__controller: AbstractController = controller
        self.__router: APIRouter = APIRouter()
        self.__routs_register()

    def __routs_register(self) -> None:
        base_register: dict = {
            "start": self.__start,
            "text_messages": self.__text_messages,
            "help": self.__help,
            "change_cerate_data": self.__change_cerate_data,
            "show_data": self.__show_data,
            "show_marks": self.__show_marks,
        }
        for path in base_register.keys():
            self.__base_register(path, base_register[path])

    def __base_register(self, path: str, endpoint: Callable) -> None:
        self.__router.add_api_route(f"/{path}", endpoint, methods=["POST"], response_model=Message)

    async def __start(self, message: Message) -> JSONResponse:
        content: dict = self.__controller.start(message)
        return JSONResponse(content=content)

    async def __text_messages(self, message: Message) -> JSONResponse:
        content: dict = self.__controller.text_messages(message)
        return JSONResponse(content=content)

    async def __help(self, message: Message) -> JSONResponse:
        content: dict = self.__controller.help(message)
        return JSONResponse(content=content)

    async def __change_cerate_data(self, message: Message) -> JSONResponse:
        content: dict = self.__controller.change_cerate_data(message)
        return JSONResponse(content=content)

    async def __show_data(self, message: Message) -> JSONResponse:
        content: dict = self.__controller.show_data(message)
        return JSONResponse(content=content)

    async def __show_marks(self, message: Message) -> JSONResponse:
        content: dict = self.__controller.show_marks(message)
        return JSONResponse(content=content)

    def get_router(self) -> APIRouter:
        return self.__router
