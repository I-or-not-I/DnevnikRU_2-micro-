"""
Модуль API для взаимодействия с парсером образовательных данных.

Предоставляет:
- Абстрактный интерфейс для работы с API
- Конкретную реализацию на базе HTTPX
- Методы для верификации данных и получения информации

Компоненты:
    AbstractApi: Абстрактный базовый класс API
    Api: Конкретная реализация API через HTTP запросы

.. note::
    Все методы работают асинхронно и используют таймауты для предотвращения зависаний.
"""

import logging
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError
import httpx
from typing import Any, Optional

from models.user_data import UserData
from models.responses import GetMarks, GetTimetable, ChangeCreateData


class AbstractApi(ABC):
    """
    Абстрактный базовый класс для API взаимодействия с парсером.

    Определяет обязательные методы, которые должны быть реализованы:
    - Верификация данных пользователя
    - Получение оценок
    - Получение расписания
    """

    @abstractmethod
    def __init__(self) -> None:
        """
        Абстрактный инициализатор API.

        :meta abstract:
        """

    @abstractmethod
    async def verify_data_get_personal_data(self, data: UserData) -> Optional[UserData]:
        """
        Абстрактный метод верификации данных и получения персональной информации.

        :param data: Данные пользователя для верификации
        :type data: UserData
        :returns: Валидированные данные пользователя или None
        :rtype: Optional[UserData]
        :meta abstract:
        """

    @abstractmethod
    async def get_marks(self, data: UserData) -> Optional[GetMarks]:
        """
        Абстрактный метод получения оценок.

        :param data: Данные пользователя для аутентификации
        :type data: UserData
        :returns: Данные об оценках или None
        :rtype: Optional[GetMarks]
        :meta abstract:
        """

    @abstractmethod
    async def get_timetable(self, data: UserData) -> Optional[GetTimetable]:
        """
        Абстрактный метод получения расписания.

        :param data: Данные пользователя для аутентификации
        :type data: UserData
        :returns: Данные расписания или None
        :rtype: Optional[GetTimetable]
        :meta abstract:
        """


class Api(AbstractApi):
    """
    Реализация API для взаимодействия с парсером через HTTP.

    :param parser_ip: IP-адрес или URL сервиса парсера
    :param timeout: Таймаут запросов в секундах
    :type parser_ip: str
    :type timeout: float
    :returns: Инициализированный экземпляр API
    :rtype: Api
    """

    def __init__(self, parser_ip: str, timeout: float) -> None:
        self.__parser_ip: str = parser_ip.rstrip("/")
        self.__timeout: float = timeout

    async def __get_data(self, path: str, data: UserData) -> Optional[Any]:
        """
        Приватный метод выполнения HTTP-запросов к парсеру.

        :param path: Конечная точка API
        :param data: Данные пользователя
        :type path: str
        :type data: UserData
        :returns: Ответ в формате JSON или None при ошибке
        :rtype: Optional[Any]
        :raises:
            - httpx.HTTPStatusError: При статусах 4xx/5xx
            - JSONDecodeError: При ошибках парсинга JSON
        :meta private:
        """
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.post(
                    f"{self.__parser_ip}/{path}", json=data.model_dump(), timeout=self.__timeout
                )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logging.info("Ошибка %s", exc)
            return None

        try:
            return response.json()
        except JSONDecodeError:
            return None

    async def verify_data_get_personal_data(self, data: UserData) -> Optional[UserData]:
        """
        Верификация данных пользователя и получение персональной информации.

        :param data: Данные пользователя для верификации
        :type data: UserData
        :returns: Валидированные данные пользователя или None
        :rtype: Optional[UserData]
        """
        get_data_response: Optional[UserData] = await self.__get_data("verify_data_get_personal_data", data)
        if get_data_response is not None:
            return UserData.model_validate(get_data_response)
        return None

    async def get_marks(self, data: UserData) -> Optional[GetMarks]:
        """
        Получение оценок пользователя.

        :param data: Данные пользователя для аутентификации
        :type data: UserData
        :returns: Данные об оценках или None
        :rtype: Optional[GetMarks]
        """
        get_data_response: Optional[GetMarks] = await self.__get_data("get_marks", data)
        if get_data_response is not None:
            return GetMarks.model_validate(get_data_response)
        return None

    async def get_timetable(self, data: UserData) -> Optional[GetTimetable]:
        """
        Получение расписания пользователя.

        :param data: Данные пользователя для аутентификации
        :type data: UserData
        :returns: Данные расписания или None
        :rtype: Optional[GetTimetable]
        """
        get_data_response: Optional[GetTimetable] = await self.__get_data("get_timetable", data)
        if get_data_response is not None:
            return GetTimetable.model_validate(get_data_response)
        return None
