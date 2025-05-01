"""
Модуль парсера данных образовательной платформы.
"""

import abc
import re
import logging
from json import dumps, loads
import requests
from bs4 import BeautifulSoup

from models.user_data import UserData


class AbstractParser(abc.ABC):
    """Абстрактный базовый класс для парсинга данных образовательной платформы.

    .. method:: get_marks(data)
        :abstractmethod:

    .. method:: get_cookies_person_school_group_id(data)
        :abstractmethod:
    """

    @staticmethod
    @abc.abstractmethod
    def get_marks(data: UserData) -> dict | bool:
        """Получение оценок пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :return: Словарь с оценками или False при ошибке
        """

    @abc.abstractmethod
    def get_cookies_person_school_group_id(self, data: UserData) -> dict | bool:
        """Получение идентификаторов и cookies сессии.

        :param data: Данные пользователя
        :type data: UserData
        :return: Словарь с данными или False при ошибке
        """


class Parser(AbstractParser):
    """Конкретная реализация парсера для работы с API образовательной платформы."""

    @staticmethod
    def get_marks(user_data: UserData) -> dict | bool:
        """Получение оценок через API платформы.

        :param user_data: Данные пользователя (должны содержать school_id, person_id и cookies)
        :type user_data: UserData
        :return: Словарь формата {предмет: [оценки, средний балл]} или False
        :raises requests.exceptions.RequestException: При ошибках сетевого запроса

        Пример возвращаемых данных:
            {
                "Математика": [["5", "4"], "4.5"],
                "Физика": [["3", "4"], "3.5"]
            }
        """
        url: str = f"https://dnevnik.ru/api/v2/marks/school/{user_data.school_id}/person/{user_data.person_id}"
        try:
            response: requests.Response = requests.get(url, cookies=user_data.cookies)
            response.raise_for_status()
            subjects: list = response.json()
        except requests.exceptions.RequestException:
            return False

        marks: dict = {}
        for subject in subjects["subjects"]:
            marks[subject["name"]] = []
            local_marks: list = []
            for work in subject["works"]:
                [local_marks.append(mark["value"]) for mark in work["marks"]]
            marks[subject["name"]].append(local_marks)
            if local_marks:
                marks[subject["name"]].append(subject["average"]["value"])

        return marks

    def get_cookies_person_school_group_id(self, user_data: UserData) -> dict | bool:
        """Получение идентификаторов и cookies через парсинг веб-страницы.

        :param user_data: Данные пользователя
        :type user_data: UserData
        :return: Словарь с данными или False при ошибке
        :raises Exception: При ошибках парсинга
        """
        session: requests.Session = self.__get_registered_session(user_data.login, user_data.password)

        try:
            html: str = session.get("https://dnevnik.ru/userfeed").text
            soup = BeautifulSoup(html, features="lxml")
            body = soup.find("body", {"class": "page-body"})
            script = body.find_all("script")[11]
            data = re.search(r"window\.__USER__START__PAGE__INITIAL__STATE__ = {(.*)}", script.text)
            initial_state = loads("{" + data[1] + "}")

            return {
                "person_id": initial_state["analytics"]["personId"],
                "school_id": initial_state["analytics"]["schoolId"],
                "group_id": initial_state["analytics"]["groupId"],
                "cookies": dumps(session.cookies.get_dict()),
            }
        except Exception as e:
            logging.error(f"Ошибка парсинга: {e}")
            return False

    @staticmethod
    def __get_registered_session(login: str, password: str) -> requests.Session:
        """Авторизация на платформе.

        :param login: Логин пользователя
        :param password: Пароль пользователя
        :return: Авторизованная сессия
        :raises requests.exceptions.RequestException: При ошибках авторизации
        """
        session = requests.Session()
        auth_data: dict = {
            "login": login,
            "password": password,
        }
        session.post("https://login.dnevnik.ru/login/esia/rostov", data=auth_data)
        return session
