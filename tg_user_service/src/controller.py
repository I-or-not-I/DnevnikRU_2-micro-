"""
Модуль контроллера для обработки команд Telegram-бота.

Предоставляет:
- Абстрактный интерфейс для обработки команд
- Конкретную реализацию бизнес-логики бота
- Интеграцию с API, шаблонами сообщений и клавиатурами

Основные функции:
- Обработка команд /start и /help
- Управление данными пользователя (регистрация, обновление)
- Получение и отображение образовательных данных (оценки, расписание)
- Формирование ответов в формате Telegram API

Компоненты:
    AbstractController: Абстрактный интерфейс контроллера
    Controller: Конкретная реализация бизнес-логики

Зависимости:
    AbstractApi: Для взаимодействия с внешними сервисами
    AbstractTemplateEngine: Для генерации текста сообщений
    AbstractMarkups: Для создания клавиатурных разметок
    Pydantic-модели: Message, UserData, GetMarks, GetTimetable и др.

.. note::
    Все методы контроллера возвращают словари в формате,
    совместимом с Telegram Bot API.
"""

import abc
import logging
from typing import Optional

from models.message import Message
from models.user_data import UserData
from models.responses import GetMarks, GetTimetable, ChangeCreateData, UserExists
from src.template_engine import AbstractTemplateEngine
from src.api import AbstractApi
from src.markups import AbstractMarkups


class AbstractController(abc.ABC):
    """
    Абстрактный базовый класс контроллера для обработки команд Telegram.

    :param api: Экземпляр API для взаимодействия с внешними сервисами
    :param template_engine: Движок шаблонов для генерации сообщений
    :param markups: Генератор клавиатурных разметок
    :type api: AbstractApi
    :type template_engine: AbstractTemplateEngine
    :type markups: AbstractMarkups
    """

    @abc.abstractmethod
    def __init__(self, api: AbstractApi, template_engine: AbstractTemplateEngine, markups: AbstractMarkups) -> None:
        """
        Абстрактный конструктор контроллера.

        :meta abstract:
        """

    @abc.abstractmethod
    async def start(self, message: Message) -> dict:
        """
        Абстрактный метод обработки команды /start.

        :param message: Входящее сообщение от пользователя
        :type message: Message
        :return: Структура ответа для Telegram API
        :rtype: dict
        :meta abstract:
        """

    @abc.abstractmethod
    async def help(self, message: Message) -> dict:
        """
        Абстрактный метод обработки команды /help.

        :param message: Входящее сообщение от пользователя
        :type message: Message
        :return: Структура ответа для Telegram API
        :rtype: dict
        :meta abstract:
        """

    @abc.abstractmethod
    async def change_create_data(self, message: Message) -> dict:
        """
        Абстрактный метод изменения или создания данных пользователя.

        :param message: Сообщение с учетными данными
        :type message: Message
        :return: Структура ответа с результатом операции
        :rtype: dict
        :meta abstract:
        """

    @abc.abstractmethod
    async def show_data(self, message: Message) -> dict:
        """
        Абстрактный метод отображения данных пользователя.

        :param message: Запрос на получение данных
        :type message: Message
        :return: Структура ответа с данными пользователя
        :rtype: dict
        :meta abstract:
        """

    @abc.abstractmethod
    async def show_marks(self, message: Message) -> dict:
        """
        Абстрактный метод отображения оценок пользователя.

        :param message: Запрос на получение оценок
        :type message: Message
        :return: Структура ответа с оценками
        :rtype: dict
        :meta abstract:
        """

    @abc.abstractmethod
    async def show_timetable(self, message: Message) -> dict:
        """
        Абстрактный метод отображения расписания занятий.

        :param message: Запрос на получение расписания
        :type message: Message
        :return: Структура ответа с расписанием
        :rtype: dict
        :meta abstract:
        """


class Controller(AbstractController):
    """
    Конкретная реализация контроллера для обработки команд Telegram.

    :param api: Экземпляр API для взаимодействия с внешними сервисами
    :param template_engine: Движок шаблонов для генерации сообщений
    :param markups: Генератор клавиатурных разметок
    :type api: AbstractApi
    :type template_engine: AbstractTemplateEngine
    :type markups: AbstractMarkups
    :returns: Инициализированный экземпляр контроллера
    :rtype: Controller
    """

    def __init__(self, api: AbstractApi, template_engine: AbstractTemplateEngine, markups: AbstractMarkups) -> None:
        logging.debug("Инициализация Controller")
        self.__template_engine: AbstractTemplateEngine = template_engine
        self.__api: AbstractApi = api
        self.__markups: AbstractMarkups = markups

    async def start(self, message: Message) -> dict:
        """
        Обработка команды /start.

        :param message: Входящее сообщение от пользователя
        :type message: Message
        :return: Структура ответа:
            - Зарегистрированным пользователям: приветствие
            - Незарегистрированным: предложение регистрации
        :rtype: dict
        """
        response: Optional[UserExists] = await self.__api.user_exists(UserData(id=message.from_.id))
        if response is None:
            return self.__server_problems(message.from_.id)
        if response.user_exists:
            return self.__base_ans(
                message.from_.id, self.__template_engine.render("registered.tfb"), self.__markups.all()
            )
        return self.__unregistered(message.from_.id, self.__markups.registration())

    async def help(self, message: Message) -> dict:
        """
        Обработка команды /help.

        :param message: Входящее сообщение от пользователя
        :type message: Message
        :return: Структура ответа с помощью
        :rtype: dict
        """
        return self.__base_ans(message.from_.id, self.__template_engine.render("help.tfb"))

    async def change_create_data(self, message: Message) -> dict:
        """
        Обработка изменения или создания данных пользователя.

        :param message: Сообщение с учетными данными (логин и пароль)
        :type message: Message
        :return: Структура ответа:
            - Успех: подтверждение сохранения
            - Ошибка: сообщение о неверных данных
        :rtype: dict
        """
        data: UserData = UserData(id=message.from_.id, login=message.login, password=message.password)
        response: Optional[ChangeCreateData] = await self.__api.change_create_data(data)
        if response is None:
            return self.__server_problems(message.from_.id)

        if response.success:
            return self.__base_ans(
                message.from_.id, self.__template_engine.render("data_saved.tfb"), self.__markups.all()
            )

        return self.__base_ans(
            message.from_.id, self.__template_engine.render("incorrect_data.tfb"), self.__markups.change_data()
        )

    async def show_data(self, message: Message) -> dict:
        """
        Отображение данных пользователя.

        :param message: Запрос на получение данных
        :type message: Message
        :return: Структура ответа:
            - Данные пользователя
            - Предупреждение для незарегистрированных
        :rtype: dict
        """
        data: Optional[UserData] = await self.__api.get_user_data(UserData(id=message.from_.id))

        if data is None:
            return self.__server_problems(message.from_.id)

        if data.login is None or data.password is None:
            return self.__unregistered(message.from_.id)
        return self.__base_ans(message.from_.id, self.__template_engine.render("user_data.tfd", data.__dict__))

    async def show_marks(self, message: Message) -> dict:
        """
        Отображение оценок пользователя.

        :param message: Запрос на получение оценок
        :type message: Message
        :return: Структура ответа:
            - Оценки пользователя
            - Предупреждение для незарегистрированных
        :rtype: dict
        """
        data: Optional[GetMarks] = await self.__api.get_marks(UserData(id=message.from_.id))
        if data is None:
            return self.__server_problems(message.from_.id)

        if data.marks is None:
            return self.__unregistered(message.from_.id)

        return self.__base_ans(message.from_.id, self.__template_engine.render("show_marks.tfb", data.marks))

    async def show_timetable(self, message: Message) -> dict:
        """
        Отображение расписания занятий.

        :param message: Запрос на получение расписания
        :type message: Message
        :return: Структура ответа с HTML-файлом расписания
        :rtype: dict
        """
        data: Optional[GetTimetable] = await self.__api.get_timetable(UserData(id=message.from_.id))
        if data is None:
            return self.__server_problems(message.from_.id)

        if data.timetable is None:
            return self.__unregistered(message.from_.id)

        return self.__file_ans(message.from_.id, data.timetable, "Расписание.html")

    def __unregistered(self, user_id: int, markup: Optional[str] = None) -> dict:
        """
        Формирование ответа для незарегистрированных пользователей.

        :param user_id: ID пользователя в Telegram
        :param markup: Разметка клавиатуры
        :type user_id: int
        :type markup: Optional[str]
        :return: Стандартная структура ответа
        :rtype: dict
        :meta private:
        """
        return self.__base_ans(user_id, self.__template_engine.render("unregistered.tfb"), markup)

    def __server_problems(self, user_id: int, markup: Optional[str] = None) -> dict:
        """
        Формирование ответа при проблемах с сервером.

        :param user_id: ID пользователя в Telegram
        :param markup: Разметка клавиатуры
        :type user_id: int
        :type markup: Optional[str]
        :return: Стандартная структура ответа
        :rtype: dict
        :meta private:
        """
        return self.__base_ans(user_id, self.__template_engine.render("server_problems.tfd"), markup)

    @staticmethod
    def __base_ans(user_id: int, message: str, markup: Optional[str] = None) -> dict:
        """
        Формирование базовой структуры ответа.

        :param user_id: ID пользователя в Telegram
        :param message: Текст сообщения
        :param markup: Опциональная разметка клавиатуры
        :type user_id: int
        :type message: str
        :type markup: Optional[str]
        :return: Стандартная структура ответа:
            {
                "user_id": int,
                "messages": [str],
                "markup": Optional[str]
            }
        :rtype: dict
        :meta private:
        """
        return {"user_id": user_id, "messages": [message], "markup": markup}

    @staticmethod
    def __file_ans(user_id: int, message: str, file_name: str, markup: Optional[str] = None) -> dict:
        """
        Формирование структуры ответа с прикрепленным файлом.

        :param user_id: ID пользователя в Telegram
        :param message: Текст сопроводительного сообщения
        :param file_name: Название файла
        :param markup: Опциональная разметка клавиатуры
        :type user_id: int
        :type message: str
        :type file_name: str
        :type markup: Optional[str]
        :return: Структура ответа с файлом:
            {
                "user_id": int,
                "message": str,
                "file_name": str,
                "markup": Optional[str]
            }
        :rtype: dict
        :meta private:
        """
        return {"user_id": user_id, "message": message, "file_name": file_name, "markup": markup}
