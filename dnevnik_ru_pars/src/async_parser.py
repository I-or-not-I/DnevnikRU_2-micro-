"""
Модуль парсера данных образовательной платформы.

Предоставляет:
- Абстрактный интерфейс для работы с платформой
- Конкретную реализацию на базе httpx и BeautifulSoup
- Методы для получения оценок, расписания и идентификаторов

Компоненты:
    AbstractParser: Абстрактный базовый класс парсера
    Parser: Конкретная реализация для работы с API и веб-страницами

.. note::
    Все методы работают асинхронно и используют таймауты.
    Для работы требуется установка дополнительных зависимостей:
    - httpx: Для HTTP-запросов
    - beautifulsoup4: Для парсинга HTML
"""

import abc
import re
import logging
from typing import Optional
from json import dumps, loads
import httpx
from bs4 import BeautifulSoup

from models.user_data import UserData


class AbstractParser(abc.ABC):
    """
    Абстрактный базовый класс для парсинга данных образовательной платформы.

    Определяет обязательные методы для:
    - Получения оценок
    - Получения расписания
    - Получения идентификаторов и cookies сессии
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        """
        Абстрактный конструктор парсера.

        :meta abstract:
        """

    @abc.abstractmethod
    async def get_marks(self, user_data: UserData) -> Optional[dict]:
        """
        Абстрактный метод получения оценок.

        :param user_data: Данные пользователя
        :type user_data: UserData
        :returns: Словарь с оценками или None
        :rtype: Optional[dict]
        :meta abstract:
        """

    @abc.abstractmethod
    async def get_timetable(self, user_data: UserData) -> Optional[str]:
        """
        Абстрактный метод получения расписания.

        :param user_data: Данные пользователя
        :type user_data: UserData
        :returns: Расписание в строковом формате или None
        :rtype: Optional[str]
        :meta abstract:
        """

    @abc.abstractmethod
    async def get_cookies_person_school_group_id(self, user_data: UserData) -> Optional[UserData]:
        """
        Абстрактный метод получения идентификаторов и cookies.

        :param user_data: Данные пользователя
        :type user_data: UserData
        :returns: Обновленные данные пользователя или None
        :rtype: Optional[UserData]
        :meta abstract:
        """


class Parser(AbstractParser):
    """
    Конкретная реализация парсера для образовательной платформы.

    :param timeout: Таймаут HTTP-запросов в секундах
    :type timeout: float
    :returns: Инициализированный экземпляр парсера
    :rtype: Parser
    """

    def __init__(self, timeout: float) -> None:
        self.__timeout: float = timeout

    async def get_marks(self, user_data: UserData) -> Optional[dict]:
        """
        Получение оценок через API платформы.

        :param user_data: Данные пользователя (должны содержать school_id, person_id и cookies)
        :type user_data: UserData
        :return: Словарь формата {предмет: [оценки, средний балл]} или None

        Пример возвращаемых данных:
            {
                "Математика": [["5", "4"], "4.5"],
                "Физика": [["3", "4"], "3.5"]
            }
        """
        url: str = f"https://dnevnik.ru/api/v2/marks/school/{user_data.school_id}/person/{user_data.person_id}"
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(
                    url, cookies=loads(str(user_data.cookies)), timeout=self.__timeout
                )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logging.warning("Ошибка парсинга оценок: %s", exc)
            return None

        marks: dict = self.__process_marks(response.json())
        return marks

    @staticmethod
    def __process_marks(data: dict) -> dict[str, list[str]]:
        """
        Приватный метод обработки данных оценок.

        :param data: Сырые данные оценок из API
        :type data: dict
        :return: Обработанные данные оценок
        :rtype: dict[str, list[str]]
        :meta private:
        """
        marks: dict = {}
        for subject in data["subjects"]:
            marks[subject["name"]] = []
            local_marks: list = []
            for work in subject["works"]:
                for mark in work["marks"]:
                    local_marks.append(mark["value"])
            marks[subject["name"]].append(local_marks)
            if local_marks:
                marks[subject["name"]].append(subject["average"]["value"])
        return marks

    async def get_timetable(self, user_data: UserData) -> Optional[str]:
        """
        Получение расписания через парсинг веб-страницы.

        :param user_data: Данные пользователя (должны содержать school_id, group_id и cookies)
        :type user_data: UserData
        :return: HTML-код расписания или текстовое сообщение об ошибке
        :rtype: Optional[str]
        """
        cookies: dict = loads(str(user_data.cookies))
        url: str = (
            f"https://schools.dnevnik.ru/v2/schedules/view?school={user_data.school_id}&group={user_data.group_id}"
        )
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(url, cookies=cookies, timeout=self.__timeout)
            soup = BeautifulSoup(response.text, features="lxml")
            url: str = soup.find("a", {"title": "Версия для печати"})["href"]
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(url, cookies=cookies, timeout=self.__timeout)
            return response.text

        except TypeError:
            return "На этой неделе у класса нет уроков"
        except httpx.HTTPStatusError as exc:
            logging.warning("Ошибка парсинга расписания: %s", exc)
            return None

    async def get_cookies_person_school_group_id(self, user_data: UserData) -> Optional[UserData]:
        """
        Получение идентификаторов и cookies через авторизацию и парсинг.

        :param user_data: Данные пользователя (должны содержать логин и пароль)
        :type user_data: UserData
        :return: Обновленные данные пользователя с идентификаторами и cookies
        :rtype: Optional[UserData]
        """
        client: httpx.AsyncClient = await self.__get_registered_client(user_data.login, user_data.password)

        try:
            response: httpx.Response = await client.get("https://dnevnik.ru/userfeed", timeout=self.__timeout)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error("Ошибка парсинга: %s", e)
            return None
        finally:
            await client.aclose()

        cookies: dict = dict(zip(client.cookies.keys(), client.cookies.values()))

        html: str = response.text
        soup = BeautifulSoup(html, features="lxml")
        body = soup.find("body", {"class": "page-body"})
        script = body.find_all("script")[11]
        data = re.search(r"window\.__USER__START__PAGE__INITIAL__STATE__ = {(.*)}", script.text)
        analytics = loads("{" + data[1] + "}")["analytics"]

        user_data.person_id = analytics["personId"]
        user_data.school_id = analytics["schoolId"]
        user_data.group_id = analytics["groupId"]
        user_data.cookies = dumps(cookies)
        return user_data

    @staticmethod
    async def __get_registered_client(login: str, password: str) -> httpx.AsyncClient:
        """
        Приватный метод авторизации на платформе.

        :param login: Логин пользователя
        :param password: Пароль пользователя
        :return: Авторизованная HTTP-сессия
        :rtype: httpx.AsyncClient
        :meta private:
        """
        url = "https://login.dnevnik.ru/login"
        auth_data: dict = {
            "login": login,
            "password": password,
        }
        client = httpx.AsyncClient()
        await client.post(url, data=auth_data)
        client.cookies.delete("dnevnik_sst")
        return client
