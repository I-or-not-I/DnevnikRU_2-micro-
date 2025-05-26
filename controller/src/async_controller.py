"""
Модуль контроллера для обработки бизнес-логики приложения.

.. note::
    Зависимости:
    - AbstractApi: Для асинхронного взаимодействия с внешним API
    - AbstractDb: Для асинхронной работы с базой данных
    - AbstractTemplateEngine: Для генерации текстовых сообщений
    - AbstractMarkups: Для создания клавиатурных разметок
"""

import abc
import logging

from models.message import Message
from models.user import User
from src.template_engine import AbstractTemplateEngine
from src.async_db import AbstractDb
from src.async_api import AbstractApi
from src.markups import AbstractMarkups


class AbstractController(abc.ABC):
    """Абстрактный базовый класс контроллера для обработки команд.

    :param api: Экземпляр API для внешних запросов
    :type api: AbstractApi
    :param db: Экземпляр базы данных
    :type db: AbstractDb
    :param template_engine: Движок шаблонов сообщений
    :type template_engine: AbstractTemplateEngine
    :param markups: Генератор разметок клавиатур
    :type markups: AbstractMarkups
    """

    @abc.abstractmethod
    def __init__(
        self, api: AbstractApi, db: AbstractDb, template_engine: AbstractTemplateEngine, markups: AbstractMarkups
    ) -> None:
        """Инициализация абстрактного контроллера."""

    @abc.abstractmethod
    async def start(self, message: Message) -> dict:
        """Обработка команды /start.

        :param message: Входящее сообщение от пользователя
        :type message: Message
        :return: Словарь с данными для формирования ответа
        :rtype: dict
        """

    @abc.abstractmethod
    async def help(self, message: Message) -> dict:
        """Обработка команды /help.

        :param message: Входящее сообщение от пользователя
        :type message: Message
        :return: Словарь с данными для формирования ответа
        :rtype: dict
        """

    @abc.abstractmethod
    async def change_create_data(self, message: Message) -> dict:
        """Обновление или создание данных пользователя.

        :param message: Сообщение с учетными данными пользователя
        :type message: Message
        :return: Словарь с результатом операции
        :rtype: dict
        """

    @abc.abstractmethod
    async def show_data(self, message: Message) -> dict:
        """Показ данных пользователя.

        :param message: Запрос на получение данных
        :type message: Message
        :return: Словарь с данными пользователя
        :rtype: dict
        """

    @abc.abstractmethod
    async def show_marks(self, message: Message) -> dict:
        """Показ оценок пользователя.

        :param message: Запрос на получение оценок
        :type message: Message
        :return: Словарь с информацией об оценках
        :rtype: dict
        """

    @abc.abstractmethod
    async def show_timetable(self, message: Message) -> dict:
        """Показ расписания пользователя.

        :param message: Запрос на получение расписания
        :type message: Message
        :return: Словарь с данными расписания
        :rtype: dict
        """


class Controller(AbstractController):
    """Конкретная реализация асинхронного контроллера.

    :param api: Экземпляр API для внешних запросов
    :type api: AbstractApi
    :param db: Экземпляр базы данных
    :type db: AbstractDb
    :param template_engine: Движок шаблонов сообщений
    :type template_engine: AbstractTemplateEngine
    :param markups: Генератор разметок клавиатур
    :type markups: AbstractMarkups
    """

    def __init__(
        self, api: AbstractApi, db: AbstractDb, template_engine: AbstractTemplateEngine, markups: AbstractMarkups
    ) -> None:
        logging.debug("Инициализация Controller")
        self.__db: AbstractDb = db
        self.__template_engine: AbstractTemplateEngine = template_engine
        self.__api: AbstractApi = api
        self.__markups: AbstractMarkups = markups

    async def start(self, message: Message) -> dict:
        """Обработка первого запуска бота.

        :param message: Сообщение с командой /start
        :type message: Message
        :return: Ответ с приветствием и клавиатурой
        :rtype: dict

        .. note::
            - Создает таблицы в БД при первом запуске
            - Проверяет регистрацию пользователя
            - Возвращает соответствующее сообщение
        """
        self.__db.create_tables()
        if await self.__db.user_exists(message.from_.id):
            return self.__base_ans(
                message.from_.id, self.__template_engine.render("registered.tfb"), self.__markups.all()
            )
        return self.__unregistered(message.from_.id, self.__markups.registration())

    async def help(self, message: Message) -> dict:
        """Возврат справочной информации.

        :param message: Сообщение с командой /help
        :type message: Message
        :return: Ответ со справочной информацией
        :rtype: dict
        """
        return self.__base_ans(message.from_.id, self.__template_engine.render("help.tfb"))

    async def change_create_data(self, message: Message) -> dict:
        """Обновление учетных данных пользователя.

        :param message: Сообщение с логином и паролем
        :type message: Message
        :return: Результат операции сохранения данных
        :rtype: dict
        """
        data: dict = {"login": message.login, "password": message.password}
        response: dict | bool = await self.__api.verify_data_get_personal_data(data)

        if not response:
            return self.__base_ans(
                message.from_.id, self.__template_engine.render("incorrect_data.tfb"), self.__markups.change_data()
            )
        data.update(response)
        if await self.__db.user_exists(message.from_.id):
            await self.__db.update_user(message.from_.id, data)
        else:
            await self.__db.create_user(message.from_.id, data)

        return self.__base_ans(message.from_.id, self.__template_engine.render("data_saved.tfb"), self.__markups.all())

    async def show_data(self, message: Message) -> dict:
        """Отображение сохраненных данных пользователя.

        :param message: Запрос на получение данных
        :type message: Message
        :return: Ответ с данными пользователя или сообщение об ошибке
        :rtype: dict
        """
        if not await self.__db.user_exists(message.from_.id):
            return self.__unregistered(message.from_.id, self.__markups.change_data())

        user: User = await self.__db.get_user(message.from_.id)
        return self.__base_ans(message.from_.id, self.__template_engine.render("user_data.tfd", user.to_dict()))

    async def show_marks(self, message: Message) -> dict:
        """Получение оценок через API.

        :param message: Запрос на получение оценок
        :type message: Message
        :return: Ответ с оценками или сообщение об ошибке
        :rtype: dict
        """
        if not await self.__db.user_exists(message.from_.id):
            return self.__unregistered(message.from_.id)

        user: User = await self.__db.get_user(message.from_.id)
        data: dict | bool = await self.__api.get_marks(user.to_dict())
        if not data:
            return self.__unregistered(message.from_.id)

        return self.__base_ans(message.from_.id, self.__template_engine.render("show_marks.tfb", data))

    async def show_timetable(self, message: Message) -> dict:
        """Получение расписания через API.

        :param message: Запрос на получение расписания
        :type message: Message
        :return: HTML-файл с расписанием или сообщение об ошибке
        :rtype: dict
        """
        if not await self.__db.user_exists(message.from_.id):
            return self.__unregistered(message.from_.id)

        user: User = await self.__db.get_user(message.from_.id)
        data: dict | bool = await self.__api.get_timetable(user.to_dict())

        if not data:
            return self.__unregistered(message.from_.id)

        return self.__file_ans(message.from_.id, data["timetable"], "Расписание.html")

    def __unregistered(self, user_id: int, markup: str = None) -> dict:
        """Формирование ответа для незарегистрированных пользователей.

        :param user_id: ID пользователя в Telegram
        :type user_id: int
        :param markup: Опциональная клавиатурная разметка
        :type markup: str, optional
        :return: Базовый ответ с предложением регистрации
        :rtype: dict
        """
        return self.__base_ans(user_id, self.__template_engine.render("unregistered.tfb"), markup)

    @staticmethod
    def __base_ans(user_id: int, message: str, markup: str = None) -> dict:
        """Формирование базового ответа.

        :param user_id: ID пользователя в Telegram
        :type user_id: int
        :param message: Текст сообщения
        :type message: str
        :param markup: Опциональная клавиатурная разметка
        :type markup: str, optional
        :return: Стандартная структура ответа
        :rtype: dict
        """
        return {"user_id": user_id, "messages": [message], "markup": markup}

    @staticmethod
    def __file_ans(user_id: int, message: str, file_name: str, markup: str = None) -> dict:
        """Формирование ответа с прикрепленным файлом.

        :param user_id: ID пользователя в Telegram
        :type user_id: int
        :param message: Текст сопроводительного сообщения
        :type message: str
        :param file_name: Название прикрепляемого файла
        :type file_name: str
        :param markup: Опциональная клавиатурная разметка
        :type markup: str, optional
        :return: Структура ответа с файлом
        :rtype: dict
        """
        return {"user_id": user_id, "message": message, "file_name": file_name, "markup": markup}
