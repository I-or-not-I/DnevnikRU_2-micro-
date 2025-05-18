"""
Модуль парсера данных образовательной платформы.
"""

import abc
import re
import logging
from json import dumps, loads
import httpx
from bs4 import BeautifulSoup

from models.user_data import UserData


class AbstractParser(abc.ABC):
    """Абстрактный базовый класс для парсинга данных образовательной платформы.

    .. method:: get_marks(data)
        :abstractmethod:

    .. method:: get_cookies_person_school_group_id(data)
        :abstractmethod:
    """

    @abc.abstractmethod
    def __init__(self):
        """Инициализация абстрактного парсера"""

    @abc.abstractmethod
    async def get_marks(self, user_data: UserData) -> dict | bool:
        """Получение оценок пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :return: Словарь с оценками или False при ошибке
        """

    @abc.abstractmethod
    async def get_timetable(self, user_data: UserData) -> dict | bool:
        """Получение расписания.

        :param data: Данные пользователя
        :type data: UserData
        :return: Словарь с расписанием или False при ошибке
        """

    @abc.abstractmethod
    async def get_cookies_person_school_group_id(self, user_data: UserData) -> dict | bool:
        """Получение идентификаторов и cookies сессии.

        :param data: Данные пользователя
        :type data: UserData
        :return: Словарь с данными или False при ошибке
        """


class Parser(AbstractParser):
    """Конкретная реализация парсера для работы с API образовательной платформы."""

    def __init__(self) -> None:
        self.__timeout: float = 10.0

    async def get_marks(self, user_data: UserData) -> dict | bool:
        """Получение оценок через API платформы.

        :param user_data: Данные пользователя (должны содержать school_id, person_id и cookies)
        :type user_data: UserData
        :return: Словарь формата {предмет: [оценки, средний балл]} или False

        Пример возвращаемых данных:
            {
                "Математика": [["5", "4"], "4.5"],
                "Физика": [["3", "4"], "3.5"]
            }
        """
        url: str = f"https://dnevnik.ru/api/v2/marks/school/{user_data.school_id}/person/{user_data.person_id}"
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(url, cookies=user_data.cookies, timeout=self.__timeout)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logging.warning("Ошибка парсинга оценок: %s", exc)
            return False

        marks: dict = self.__process_marks(response.json())

        return marks

    @staticmethod
    def __process_marks(data: dict) -> dict[str, list[str]]:
        """Обработка данных оценок"""
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

    async def get_timetable(self, user_data: UserData) -> dict | bool:
        url: str = (
            f"https://schools.dnevnik.ru/v2/schedules/view?school={user_data.school_id}&group={user_data.group_id}"
        )
        try:
            async with httpx.AsyncClient() as client:
                response: httpx.Response = await client.get(url, cookies=user_data.cookies, timeout=self.__timeout)
            html: str = response.text
            soup = BeautifulSoup(html, features="lxml")
            url: str = soup.find("a", {"title": "Версия для печати"})["href"]
            async with httpx.AsyncClient() as client:
                response: str = await client.get(url, cookies=user_data.cookies, timeout=self.__timeout)
            html: str = response.text
            return {"timetable": html}
        except httpx.HTTPStatusError as exc:
            logging.warning("Ошибка парсинга расписания: %s", exc)
            return False

    async def get_cookies_person_school_group_id(self, user_data: UserData) -> dict | bool:
        """Получение идентификаторов и cookies через парсинг веб-страницы.

        :param user_data: Данные пользователя
        :type user_data: UserData
        :return: Словарь с данными или False при ошибке
        """

        client: httpx.AsyncClient = await self.__get_registered_client(user_data.login, user_data.password)

        try:
            response: httpx.Response = await client.get("https://dnevnik.ru/userfeed", timeout=self.__timeout)
        except httpx.HTTPStatusError as e:
            client.aclose()
            logging.error("Ошибка парсинга: %s", e)
            return False

        cookies: dict = dict(zip(client.cookies.keys(), client.cookies.values()))
        client.aclose()

        html: str = response.text
        soup = BeautifulSoup(html, features="lxml")
        body = soup.find("body", {"class": "page-body"})
        script = body.find_all("script")[11]
        data = re.search(r"window\.__USER__START__PAGE__INITIAL__STATE__ = {(.*)}", script.text)
        initial_state = loads("{" + data[1] + "}")
        return {
            "person_id": initial_state["analytics"]["personId"],
            "school_id": initial_state["analytics"]["schoolId"],
            "group_id": initial_state["analytics"]["groupId"],
            "cookies": dumps(cookies),
        }

    @staticmethod
    async def __get_registered_client(login: str, password: str) -> httpx.AsyncClient:
        """Авторизация на платформе.

        :param login: Логин пользователя
        :param password: Пароль пользователя
        :return: Авторизованная сессия
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
