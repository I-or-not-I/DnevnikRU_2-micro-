"""
Модуль API для взаимодействия с парсером данных.
"""

import abc
import requests
from json import dumps


class AbstractApi(abc.ABC):
    """Абстрактный базовый класс для API взаимодействия с парсером.

    .. method:: verify_data_get_personal_data(data)
        :abstractmethod:

    .. method:: get_marks(data)
        :abstractmethod:
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        """Инициализация API."""

    @abc.abstractmethod
    def verify_data_get_personal_data(self, data: dict) -> dict | bool:
        """Верификация данных и получение персональной информации.

        :param data: Словарь с учетными данными
        :type data: dict["login": str, "password": str]
        :return: Данные пользователя или False при ошибке
        :rtype: dict | bool
        """

    @abc.abstractmethod
    def get_marks(self, data: dict) -> dict | bool:
        """Получение информации об оценках.

        :param data: Данные для запроса оценок
        :type data: dict
        :return: Словарь с оценками или False при ошибке
        :rtype: dict | bool
        """


class Api(AbstractApi):
    """Конкретная реализация API для работы с парсером через HTTP.

    :param parser_ip: IP-адрес или URL сервиса парсера
    :type parser_ip: str
    """

    def __init__(self, parser_ip: str) -> None:
        self.__parser_ip: str = parser_ip.rstrip("/")

    def __get_data(self, path: str, data: dict) -> dict | bool:
        """Приватный метод выполнения POST-запросов.

        :param path: Конечная точка API
        :param data: Данные для отправки
        :type path: str
        :type data: dict
        :return: Ответ сервера или False при ошибке
        :rtype: dict | bool
        :raises requests.exceptions.HTTPError: При ошибках HTTP
        :meta private:
        """
        try:
            response: requests.Response = requests.post(
                f"{self.__parser_ip}/{path}", data=self.__dict_to_json(data), timeout=5
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return False

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return False

    def verify_data_get_personal_data(self, data: dict) -> dict | bool:
        """Реализация метода верификации данных.

        Использует эндпоинт /verify_data_get_personal_data
        """
        return self.__get_data("verify_data_get_personal_data", data)

    def get_marks(self, data: dict) -> dict | bool:
        """Реализация метода получения оценок.

        Использует эндпоинт /get_marks
        """
        return self.__get_data("get_marks", data)

    @staticmethod
    def __dict_to_json(data: dict) -> str:
        """Конвертация словаря в JSON-строку.

        :param data: Данные для конвертации
        :type data: dict
        :return: JSON-строка
        :rtype: str
        :meta private:
        """
        return dumps(data, ensure_ascii=False)
