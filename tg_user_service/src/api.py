"""
Модуль API для взаимодействия с парсером данных образовательной платформы.

Предоставляет:
- Абстрактный интерфейс для работы с API
- Конкретную реализацию на базе HTTPX
- Методы для взаимодействия с образовательными данными

Компоненты:
    AbstractApi: Абстрактный базовый класс API
    Api: Конкретная реализация API через HTTP запросы

.. note::
    Все методы работают асинхронно и используют таймауты.
    Ответы API валидируются через Pydantic-модели.
"""

import logging
import abc
from json import decoder
from typing import Optional, Any
import httpx

from models.user_data import UserData
from models.responses import GetMarks, GetTimetable, ChangeCreateData, UserExists


class AbstractApi(abc.ABC):
    """
    Абстрактный базовый класс для API взаимодействия с парсером.

    Определяет обязательные методы:
    - Изменение/создание данных
    - Проверка существования пользователя
    - Получение данных пользователя
    - Получение оценок
    - Получение расписания
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        """
        Абстрактный инициализатор API.

        :meta abstract:
        """

    @abc.abstractmethod
    async def change_create_data(self, data: UserData) -> ChangeCreateData:
        """
        Абстрактный метод изменения или создания данных пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Статус операции
        :rtype: ChangeCreateData
        :meta abstract:
        """
        pass

    @abc.abstractmethod
    async def user_exists(self, data: UserData) -> UserExists:
        """
        Абстрактный метод проверки существования пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Статус существования пользователя
        :rtype: UserExists
        :meta abstract:
        """
        pass

    @abc.abstractmethod
    async def get_user_data(self, data: UserData) -> UserData:
        """
        Абстрактный метод получения данных пользователя.

        :param data: Данные пользователя для идентификации
        :type data: UserData
        :returns: Полные данные пользователя
        :rtype: UserData
        :meta abstract:
        """
        pass

    @abc.abstractmethod
    async def get_marks(self, data: UserData) -> GetMarks:
        """
        Абстрактный метод получения оценок.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Данные об оценках
        :rtype: GetMarks
        :meta abstract:
        """
        pass

    @abc.abstractmethod
    async def get_timetable(self, data: UserData) -> GetTimetable:
        """
        Абстрактный метод получения расписания.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Данные расписания
        :rtype: GetTimetable
        :meta abstract:
        """
        pass


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
        except decoder.JSONDecodeError:
            return None

    async def change_create_data(self, data: UserData) -> Optional[ChangeCreateData]:
        """
        Изменение или создание данных пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Статус операции или None при ошибке
        :rtype: Optional[ChangeCreateData]
        """
        get_data_response: Optional[ChangeCreateData] = await self.__get_data("change_create_data", data)
        if get_data_response is not None:
            return ChangeCreateData.model_validate(get_data_response)
        return None

    async def user_exists(self, data: UserData) -> Optional[UserExists]:
        """
        Проверка существования пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Статус существования или None при ошибке
        :rtype: Optional[UserExists]
        """
        get_data_response: Optional[UserExists] = await self.__get_data("user_exists", data)
        if get_data_response is not None:
            return UserExists.model_validate(get_data_response)
        return None

    async def get_user_data(self, data: UserData) -> Optional[UserData]:
        """
        Получение полных данных пользователя.

        :param data: Данные пользователя для идентификации
        :type data: UserData
        :returns: Полные данные пользователя или None при ошибке
        :rtype: Optional[UserData]
        """
        get_data_response: Optional[UserData] = await self.__get_data("get_user_data", data)
        if get_data_response is not None:
            return UserData.model_validate(get_data_response)
        return None

    async def get_marks(self, data: UserData) -> Optional[GetMarks]:
        """
        Получение оценок пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Данные об оценках или None при ошибке
        :rtype: Optional[GetMarks]
        """
        get_data_response: Optional[GetMarks] = await self.__get_data("get_marks", data)
        if get_data_response is not None:
            return GetMarks.model_validate(get_data_response)
        return None

    async def get_timetable(self, data: UserData) -> Optional[GetTimetable]:
        """
        Получение расписания пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Данные расписания или None при ошибке
        :rtype: Optional[GetTimetable]
        """
        get_data_response: Optional[GetTimetable] = await self.__get_data("get_timetable", data)
        if get_data_response is not None:
            return GetTimetable.model_validate(get_data_response)
        return None
