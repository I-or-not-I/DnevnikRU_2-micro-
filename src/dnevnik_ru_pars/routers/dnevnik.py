from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable

from routers.abstract import AbstractRouter
from models.user_data import UserData
from src.parser import AbstractParser


class Router(AbstractRouter):
    def __init__(self, parser: AbstractParser) -> None:
        self.__parser: AbstractParser = parser
        self.__router: APIRouter = APIRouter()
        self.__routs_register()

    def __routs_register(self) -> None:
        base_register: dict = {
            "get_marks": self.__get_marks,
            "verify_data_get_personal_data": self.__verify_data_get_personal_data,
        }
        for path in base_register.keys(): self.__base_register(path, base_register[path])

    def __base_register(self, path: str, endpoint: Callable) -> None:
        self.__router.add_api_route(f"/{path}", endpoint, methods=["POST"], response_model=UserData)

    async def __get_marks(self, data: UserData) -> JSONResponse:
        content: dict = self.__parser.get_marks(data)
        if not content:
            raise HTTPException(status_code=400)
        return JSONResponse(content=content)

    async def __verify_data_get_personal_data(self, data: UserData) -> JSONResponse:
        content: dict = self.__parser.get_cookies_person_school_group_id(data)
        if not content:
            raise HTTPException(status_code=400)
        return JSONResponse(content=content)

    def get_router(self) -> APIRouter:
        return self.__router
