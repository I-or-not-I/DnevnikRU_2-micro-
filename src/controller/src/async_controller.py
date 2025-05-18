"""
Модуль контроллера для обработки бизнес-логики приложения.

.. moduleauthor:: Ваше имя <ваш@email>

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
from src.template_engine import AbstractTemplateEngine
from src.async_db import AbstractDb
from src.async_api import AbstractApi
from src.markups import AbstractMarkups


class AbstractController(abc.ABC):
    """Абстрактный базовый класс контроллера для обработки команд.

    :param api: Экземпляр API для внешних запросов
    :param db: Экземпляр базы данных
    :param template_engine: Движок шаблонов сообщений
    :param markups: Генератор разметок клавиатур
    """

    @abc.abstractmethod
    def __init__(
        self, api: AbstractApi, db: AbstractDb, template_engine: AbstractTemplateEngine, markups: AbstractMarkups
    ) -> None:
        """Инициализация Abstract."""

    @abc.abstractmethod
    async def start(self, message: Message) -> dict:
        """Обработка команды /start."""

    @abc.abstractmethod
    async def help(self, message: Message) -> dict:
        """Обработка команды /help."""

    @abc.abstractmethod
    async def change_create_data(self, message: Message) -> dict:
        """Обновление или создание данных пользователя."""

    @abc.abstractmethod
    async def show_data(self, message: Message) -> dict:
        """Показ данных пользователя."""

    @abc.abstractmethod
    async def show_marks(self, message: Message) -> dict:
        """Показ оценок пользователя."""

    @abc.abstractmethod
    async def show_timetable(self, message: Message) -> dict:
        """Показ расписания пользователя."""


class Controller(AbstractController):
    """Конкретная реализация асинхронного контроллера."""

    def __init__(
        self, api: AbstractApi, db: AbstractDb, template_engine: AbstractTemplateEngine, markups: AbstractMarkups
    ) -> None:
        logging.debug("Инициализация Controller")
        self.__db: AbstractDb = db
        self.__template_engine: AbstractTemplateEngine = template_engine
        self.__api: AbstractApi = api
        self.__markups: AbstractMarkups = markups

    async def start(self, message: Message) -> dict:
        """Асинхронная обработка первого запуска бота."""
        if await self.__db.user_in_table(message.from_.id):
            return self.__base_ans(
                message.from_.id, self.__template_engine.render("registered.tfb"), self.__markups.all()
            )
        return self.__unregistered(message.from_.id, self.__markups.registration())

    async def help(self, message: Message) -> dict:
        """Асинхронный возврат справочной информации."""
        return self.__base_ans(message.from_.id, self.__template_engine.render("help.tfb"))

    async def change_create_data(self, message: Message) -> dict:
        """Асинхронное обновление учетных данных."""
        data: dict = {"login": message.login, "password": message.password}
        response: dict | bool = await self.__api.verify_data_get_personal_data(data)

        if not response:
            return self.__base_ans(
                message.from_.id, self.__template_engine.render("incorrect_data.tfb"), self.__markups.change_data()
            )

        data.update(response)
        if await self.__db.user_in_table(message.from_.id):
            await self.__db.update_user_data(message.from_.id, data)
        else:
            await self.__db.create_new_user(message.from_.id, data)

        return self.__base_ans(message.from_.id, self.__template_engine.render("data_saved.tfb"), self.__markups.all())

    async def show_data(self, message: Message) -> dict:
        """Асинхронное получение и отображение данных."""
        if not await self.__db.user_in_table(message.from_.id):
            return self.__unregistered(message.from_.id, self.__markups.change_data())

        user_data: dict = await self.__db.get_user_data(message.from_.id)
        return self.__base_ans(message.from_.id, self.__template_engine.render("user_data.tfd", user_data))

    async def show_marks(self, message: Message) -> dict:
        """Асинхронное получение оценок."""
        if not await self.__db.user_in_table(message.from_.id):
            return self.__unregistered(message.from_.id)

        user_data: dict = await self.__db.get_user_data(message.from_.id)
        data: dict | bool = await self.__api.get_marks(user_data)

        if not data:
            return self.__unregistered(message.from_.id)

        return self.__base_ans(message.from_.id, self.__template_engine.render("show_marks.tfb", data))

    async def show_timetable(self, message: Message) -> dict:
        """Асинхронное получение расписания."""
        if not await self.__db.user_in_table(message.from_.id):
            return self.__unregistered(message.from_.id)

        user_data: dict = await self.__db.get_user_data(message.from_.id)
        data: dict | bool = await self.__api.get_timetable(user_data)

        if not data:
            return self.__unregistered(message.from_.id)

        return self.__file_ans(message.from_.id, data["timetable"], "Расписание.html")

    def __unregistered(self, user_id: int, markup: str = None) -> dict:
        """Вспомогательный метод для незарегистрированных пользователей."""
        return self.__base_ans(user_id, self.__template_engine.render("unregistered.tfb"), markup)

    @staticmethod
    def __base_ans(user_id: int, message: str, markup: str = None) -> dict:
        """Базовый формат ответа."""
        return {"user_id": user_id, "messages": [message], "markup": markup}

    @staticmethod
    def __file_ans(user_id: int, message: str, file_name: str, markup: str = None) -> dict:
        """Формат ответа с файлом."""
        return {"user_id": user_id, "message": message, "file_name": file_name, "markup": markup}
