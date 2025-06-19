"""
Модуль роутера для работы с образовательными данными.

Предоставляет API-эндпоинты для:
- Получения оценок
- Получения расписания
- Проверки существования пользователя
- Создания/обновления данных пользователя

Основные компоненты:
    Router: Класс роутера, регистрирующий эндпоинты и обрабатывающий запросы.

Зависимости:
    AbstractRouter: Абстрактный базовый класс для роутеров
    AbstractApi, AbstractDb: Абстракции для работы с API и базой данных
    Pydantic-модели: UserData, User, GetMarks, GetTimetable, UserExists, ChangeCreateData

.. note::
    Все эндпоинты принимают данные в формате UserData через POST-запросы.
"""

from typing import Callable, Optional
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from routers.abstract import AbstractRouter
from src.api import AbstractApi
from src.db import AbstractDb
from models.user_data import UserData
from models.user import User
from models.responses import GetMarks, GetTimetable, UserExists, ChangeCreateData


class Router(AbstractRouter):
    """
    Реализация роутера для образовательных данных.

    :param api: Экземпляр API для взаимодействия с внешним сервисом
    :param db: Экземпляр базы данных для работы с хранилищем
    :type api: AbstractApi
    :type db: AbstractDb
    :returns: Инициализированный экземпляр роутера
    :rtype: Router
    """

    def __init__(self, api: AbstractApi, db: AbstractDb) -> None:
        self.__router: APIRouter = APIRouter()
        self.__api: AbstractApi = api
        self.__db: AbstractDb = db

        self.__register_paths: dict = {
            "get_marks": self.__get_marks,
            "get_timetable": self.__get_timetable,
            "user_exists": self.__user_exists,
            "change_create_data": self.__change_create_data,
        }

        self.__routs_register()

    def __routs_register(self) -> None:
        """Приватный метод регистрации маршрутов.

        :meta private:
        """
        for path, endpoint in self.__register_paths.items():
            self.__base_register(path, endpoint)

    def __base_register(self, path: str, endpoint: Callable) -> None:
        """Базовый регистратор эндпоинтов.

        :param path: URL путь для эндпоинта
        :param endpoint: Обработчик запроса
        :type path: str
        :type endpoint: Callable
        :meta private:
        """
        self.__router.add_api_route(f"/{path}", endpoint, methods=["POST"])

    async def __get_marks(self, data: UserData) -> JSONResponse:
        """
        Обработчик запроса оценок пользователя.

        :param data: Данные пользователя для аутентификации
        :type data: UserData
        :returns: Ответ с оценками в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        user_data: Optional[User] = await self.__db.get_user(data)
        if user_data is None:
            return JSONResponse(content=GetMarks().model_dump())
        content: Optional[GetMarks] = await self.__api.get_marks(UserData.model_validate(user_data))
        if content is not None:
            return JSONResponse(content=content.model_dump())
        return JSONResponse(content=GetMarks().model_dump())

    async def __get_timetable(self, data: UserData) -> JSONResponse:
        """
        Обработчик запроса расписания пользователя.

        :param data: Данные пользователя для аутентификации
        :type data: UserData
        :returns: Ответ с расписанием в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        user_data: Optional[User] = await self.__db.get_user(data)
        if user_data is None:
            return JSONResponse(content=GetTimetable().model_dump())
        content: Optional[GetTimetable] = await self.__api.get_timetable(UserData.model_validate(user_data.to_dict()))
        if content is not None:
            return JSONResponse(content=content.model_dump())
        return JSONResponse(content=GetTimetable().model_dump())

    async def __user_exists(self, data: UserData) -> JSONResponse:
        """
        Обработчик проверки существования пользователя.

        :param data: Данные пользователя для проверки
        :type data: UserData
        :returns: Ответ с результатом проверки в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        content: Optional[UserExists] = UserExists(user_exists=await self.__db.user_exists(data))
        return JSONResponse(content=content.model_dump())

    async def __change_create_data(self, data: UserData) -> JSONResponse:
        """
        Обработчик создания/обновления данных пользователя.

        :param data: Данные пользователя для создания/обновления
        :type data: UserData
        :returns: Ответ с результатом операции в формате JSON
        :rtype: JSONResponse
        :meta private:
        """
        user_data: Optional[UserData] = await self.__api.verify_data_get_personal_data(data)
        if user_data is None:
            return JSONResponse(content=ChangeCreateData(success=False).model_dump())
        content: ChangeCreateData = ChangeCreateData(success=await self.__db.create_update_user(user_data))
        return JSONResponse(content=content.model_dump())

    def get_router(self) -> APIRouter:
        """
        Получение роутера с зарегистрированными эндпоинтами.

        :return: Готовый к использованию APIRouter
        :rtype: :class:`APIRouter`
        """
        return self.__router

    def get_endpoints(self) -> tuple:
        """
        Получение списка всех доступных эндпоинтов.

        :return: Кортеж с именами эндпоинтов
        :rtype: tuple
        """
        return tuple(self.__register_paths.keys())
