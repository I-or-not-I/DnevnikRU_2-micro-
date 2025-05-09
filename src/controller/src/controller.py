"""
Модуль контроллера для обработки бизнес-логики приложения.

.. moduleauthor:: Ваше имя <ваш@email>

.. note::
    Зависимости:
    - AbstractApi: Для взаимодействия с внешним API
    - AbstractDb: Для работы с базой данных
    - AbstractTemplateEngine: Для генерации текстовых сообщений
    - AbstractMarkups: Для создания клавиатурных разметок
"""

import abc
import logging
from models.message import Message
from src.template_engine import AbstractTemplateEngine
from src.db import AbstractDb
from src.api import AbstractApi
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
    def start(self, message: Message) -> dict:
        """Обработка команды /start.

        :param message: Входящее сообщение
        :type message: Message
        :return: Ответ в формате {user_id, messages, markup}
        """

    @abc.abstractmethod
    def help(self, message: Message) -> dict:
        """Обработка команды /help."""

    @abc.abstractmethod
    def change_create_data(self, message: Message) -> dict:
        """Обновление или создание данных пользователя."""

    @abc.abstractmethod
    def show_data(self, message: Message) -> dict:
        """Показ данных пользователя."""

    @abc.abstractmethod
    def show_marks(self, message: Message) -> dict:
        """Показ оценок пользователя."""

    @abc.abstractmethod
    def show_timetable(self, message: Message) -> dict:
        """Показ расписания пользователя."""


class Controller(AbstractController):
    """Конкретная реализация контроллера.

    :param api: Реализация AbstractApi
    :param db: Реализация AbstractDb
    :param template_engine: Реализация AbstractTemplateEngine
    :param markups: Реализация AbstractMarkups
    """

    def __init__(
        self, api: AbstractApi, db: AbstractDb, template_engine: AbstractTemplateEngine, markups: AbstractMarkups
    ) -> None:
        logging.debug("Инициализация Controller")
        self.__db: AbstractDb = db
        self.__template_engine: AbstractTemplateEngine = template_engine
        self.__api: AbstractApi = api
        self.__markups: AbstractMarkups = markups

    def start(self, message: Message) -> dict:
        """Обработка первого запуска бота.

        .. note::
            Логика:
            1. Проверка регистрации пользователя
            2. Возврат соответствующего шаблона:
               - registered.tfb для зарегистрированных
               - unregistered.tfb для новых пользователей
        """
        if self.__db.user_in_table(message.from_.id):
            return self.__base_ans(
                message.from_.id, self.__template_engine.render("registered.tfb"), self.__markups.all()
            )
        return self.__unregistered(message.from_.id, self.__markups.registration())

    def help(self, message: Message) -> dict:
        """Возвращает справочную информацию."""
        return self.__base_ans(message.from_.id, self.__template_engine.render("help.tfb"))

    def change_create_data(self, message: Message) -> dict:
        """Обновление учетных данных пользователя."""
        data: dict = {"login": message.login, "password": message.password}
        response: dict | bool = self.__api.verify_data_get_personal_data(data)
        if not response:
            ans_message: str = self.__template_engine.render("incorrect_data.tfb")
            markup: str = self.__markups.change_data()
            return self.__base_ans(message.from_.id, ans_message, markup)

        data.update(response)
        if self.__db.user_in_table(message.from_.id):
            self.__db.update_user_data(message.from_.id, data)
        else:
            self.__db.create_new_user(message.from_.id, data)
        ans_message: str = self.__template_engine.render("data_saved.tfb")
        markup: str = self.__markups.all()
        return self.__base_ans(message.from_.id, ans_message, markup)

    def show_data(self, message: Message) -> dict:
        """Отображение персональных данных."""
        if not self.__db.user_in_table(message.from_.id):
            return self.__unregistered(message.from_.id, self.__markups.change_data)

        return self.__base_ans(
            message.from_.id, self.__template_engine.render("user_data.tfd", self.__db.get_user_data(message.from_.id))
        )

    def show_marks(self, message: Message) -> dict:
        """Получение и отображение оценок."""
        if not self.__db.user_in_table(message.from_.id):
            return self.__unregistered(message.from_.id)

        if not (data := self.__api.get_marks(self.__db.get_user_data(message.from_.id))):
            return self.__unregistered(message.from_.id)

        return self.__base_ans(message.from_.id, self.__template_engine.render("show_marks.tfb", data))

    def show_timetable(self, message: Message) -> dict:
        """Получение и отображение расписания."""
        if not self.__db.user_in_table(message.from_.id):
            return self.__unregistered(message.from_.id)

        if not (data := self.__api.get_timetable(self.__db.get_user_data(message.from_.id))):
            return self.__unregistered(message.from_.id)

        return self.__file_ans(message.from_.id, data["timetable"], "Расписание.html")

    def __unregistered(self, user_id: int, markup: str = None) -> dict:
        """Вспомогательный метод для незарегистрированных пользователей.

        :meta private:
        """
        return self.__base_ans(user_id, self.__template_engine.render("unregistered.tfb"), markup)

    @staticmethod
    def __base_ans(user_id: int, message: str, markup: str = None) -> dict:
        """Базовый формат ответа.

        :meta private:
        :return: {"user_id": int, "messages": List[str], "markup": Optional[str]}
        """
        return {"user_id": user_id, "messages": [message], "markup": markup}

    @staticmethod
    def __file_ans(user_id: int, message: str, file_name: str, markup: str = None) -> dict:
        """Базовый формат ответа для файла(str).

        :meta private:
        :return: {"user_id": int, "message": str, "markup": Optional[str]}
        """
        return {"user_id": user_id, "message": message, "file_name": file_name, "markup": markup}