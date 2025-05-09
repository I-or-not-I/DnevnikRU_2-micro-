"""
Модуль API для взаимодействия с контроллером.

Модуль содержит:
- AbstractApi - абстрактный базовый класс API
- Api - реализацию API
"""

import logging
import abc
import requests
from urllib.parse import urljoin
from telebot import types


class AbstractApi(abc.ABC):
    """Абстрактный базовый класс для API взаимодействия с контроллером.

    :param controller_ip: Базовый URL контроллера
    :type controller_ip: str

    .. method:: start(message)
        :abstractmethod:

    .. method:: help(message)
        :abstractmethod:

    .. method:: change_create_data(message, login, password)
        :abstractmethod:

    .. method:: show_data(message)
        :abstractmethod:

    .. method:: show_marks(message)
        :abstractmethod:
    """

    @abc.abstractmethod
    def __init__(self, controller_ip: str) -> None:
        pass

    @abc.abstractmethod
    def start(self, message: types.Message) -> dict:
        """Обработка команды запуска бота.

        :param message: Входящее сообщение от пользователя
        :type message: types.Message
        :return: Ответ сервера с приветственной информацией
        :rtype: dict
        """

    @abc.abstractmethod
    def help(self, message: types.Message) -> dict:
        """Помощь администратора.

        :param message: Входящее сообщение от пользователя
        :type message: types.Message
        :return: Ответ сервера с ссылкой на администратора
        :rtype: dict
        """

    @abc.abstractmethod
    def change_create_data(self, message: types.Message, login: str, password: str) -> dict:
        """Обновление учетных данных пользователя.

        :param message: Входящее сообщение от пользователя
        :param login: Новый логин для системы
        :param password: Новый пароль для системы
        :type message: types.Message
        :type login: str
        :type password: str
        :return: Результат обновления данных
        :rtype: dict
        """

    @abc.abstractmethod
    def show_data(self, message: types.Message) -> dict:
        """Получить персональные данные пользователя.

        :param message: Входящее сообщение от пользователя
        :type message: types.Message
        :return: Данные пользователя из системы
        :rtype: dict
        """

    @abc.abstractmethod
    def show_marks(self, message: types.Message) -> dict:
        """Получить информацию об оценках.

        :param message: Входящее сообщение от пользователя
        :type message: types.Message
        :return: Данные об оценках из системы
        :rtype: dict
        """

    @abc.abstractmethod
    def show_timetable(self, message: types.Message) -> dict:
        """Получить информацию о расписании.

        :param message: Входящее сообщение от пользователя
        :type message: types.Message
        :return: Данные о расписании из системы
        :rtype: dict
        """


class Api(AbstractApi):
    """Конкретная реализация API с использованием HTTP-протокола.

    :param controller_ip: Базовый URL контроллера
    :type controller_ip: str

    .. attribute:: __controller_ip
        :annotation: = приватное поле с URL контроллера

    .. method:: __get_data(path, message, data=None)
        :private:

    .. method:: __error_message(message)
        :private:
    """

    def __init__(self, controller_ip: str) -> None:
        self.__controller_ip: str = controller_ip.rstrip("/")
        self.__timeout: int = 5

    def __get_data(self, path: str, message: types.Message, data: dict = None) -> dict:
        """Основной метод выполнения запросов к API.

        :param path: Конечная точка API
        :param message: Объект сообщения Telegram
        :param data: Дополнительные данные для запроса
        :type path: str
        :type message: types.Message
        :type data: dict, optional
        :return: Ответ API или сообщение об ошибке
        :rtype: dict
        """
        try:
            url: str = urljoin(f"{self.__controller_ip}/", path)
            json_data: dict = data if data else message.json
            response: requests.Response = requests.post(url, json=json_data, timeout=self.__timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка запроса: {e}")
            return self.__error_message(message)
        except Exception as e:
            logging.error(f"Непредвиденная ошибка: {e}")
            return self.__error_message(message)

    def start(self, message: types.Message) -> dict:
        """Реализация метода запуска бота"""
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: start")
        return self.__get_data("start", message)

    def help(self, message: types.Message) -> dict:
        """Реализация метода помощи"""
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: help")
        return self.__get_data("help", message)

    def change_create_data(self, message: types.Message, login: str, password: str) -> dict:
        """Реализация обновления данных с добавлением учетных данных."""
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: change_create_data")
        data: dict = message.json
        data.update({"login": login, "password": password})
        return self.__get_data("change_create_data", message, data)

    def show_data(self, message: types.Message) -> dict:
        """Реализация запроса персональных данных."""
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: show_data")
        return self.__get_data("show_data", message)

    def show_marks(self, message: types.Message) -> dict:
        """Реализация запроса информации об оценках."""
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: show_marks")
        return self.__get_data("show_marks", message)

    def show_timetable(self, message: types.Message) -> dict:
        """Реализация запроса информации о расписании."""
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: show_timetable")
        return self.__get_data("show_timetable", message)

    @staticmethod
    def __error_message(message: types.Message) -> dict:
        """Формирование стандартного сообщения об ошибке.

        :param message: Исходное сообщение пользователя
        :type message: types.Message
        :return: Стандартная ошибка
        :rtype: dict
        """
        return {"user_id": message.from_user.id, "messages": ["Проблемы с сервером, попробуйте позже"], "markup": None}
