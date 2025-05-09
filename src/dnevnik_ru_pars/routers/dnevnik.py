"""
Модуль роутера для работы с образовательными данными.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable
from routers.abstract import AbstractRouter
from models.user_data import UserData
from src.parser import AbstractParser


class Router(AbstractRouter):
    """Конкретная реализация роутера для работы с образовательными данными.

    Наследует:
    - :class:`AbstractRouter`

    :param parser: Парсер
    :type parser: :class:`AbstractParser`
    """

    def __init__(self, parser: AbstractParser) -> None:
        self.__parser: AbstractParser = parser
        self.__router: APIRouter = APIRouter()
        self.__routs_register()

    def __routs_register(self) -> None:
        """Приватный метод регистрации маршрутов.

        :meta private:
        """
        base_register: dict = {
            "get_marks": self.__get_marks,
            "get_timetable": self.__get_timetable,
            "verify_data_get_personal_data": self.__verify_data_get_personal_data,
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
        self.__router.add_api_route(f"/{path}", endpoint, methods=["POST"], response_model=UserData)

    async def __get_marks(self, data: UserData) -> JSONResponse:
        """Эндпоинт для получения оценок.

        :param data: Данные пользователя
        :type data: :class:`UserData`
        :return: JSON с оценками
        :rtype: :class:`JSONResponse`
        :raises HTTPException: 400 если данные некорректны
        """
        content: dict = self.__parser.get_marks(data)
        if not content:
            raise HTTPException(status_code=400)
        return JSONResponse(content=content)

    async def __get_timetable(self, data: UserData) -> JSONResponse:
        """Эндпоинт для получения расписания.

        :param data: Данные пользователя
        :type data: :class:`UserData`
        :return: JSON с расписанием
        :rtype: :class:`JSONResponse`
        :raises HTTPException: 400 если данные некорректны
        """
        content: dict = self.__parser.get_timetable(data)
        if not content:
            raise HTTPException(status_code=400)
        return JSONResponse(content=content)

    async def __verify_data_get_personal_data(self, data: UserData) -> JSONResponse:
        """Эндпоинт для верификации данных и получения персональной информации.

        :param data: Данные пользователя
        :type data: :class:`UserData`
        :return: JSON с персональными данными
        :rtype: :class:`JSONResponse`
        :raises HTTPException: 400 если верификация не пройдена
        """
        content: dict = self.__parser.get_cookies_person_school_group_id(data)
        if not content:
            raise HTTPException(status_code=400)
        return JSONResponse(content=content)

    def get_router(self) -> APIRouter:
        """Получение роутера с зарегистрированными эндпоинтами.

        :return: Готовый к использованию APIRouter
        :rtype: :class:`APIRouter`
        """
        return self.__router
