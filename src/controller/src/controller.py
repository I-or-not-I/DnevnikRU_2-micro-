import abc
import logging

from models.message import Message
from src.template_engine import AbstractTemplateEngine
from src.db import AbstractDb
from src.api import AbstractApi
from src.markups import AbstractMarkups


class AbstractController(abc.ABC):
    @abc.abstractmethod
    def __init__(self, api: AbstractApi, db: AbstractDb, template_engine: AbstractTemplateEngine, markups: AbstractMarkups) -> None:
        logging.debug("Инициализация Controller")

    @abc.abstractmethod
    def start(message: Message) -> dict:
        logging.debug("Запрос start пользователем {message.from_.id}")

    @abc.abstractmethod
    def help(message: Message) -> dict:
        logging.debug("Запрос help пользователем {message.from_.id}")

    @abc.abstractmethod
    def change_cerate_data(message: Message) -> dict:
        logging.debug("Запрос change_cerate_data пользователем {message.from_.id}")

    @abc.abstractmethod
    def show_data(message: Message) -> dict:
        logging.debug("Запрос show_data пользователем {message.from_.id}")

    @abc.abstractmethod
    def show_marks(message: Message) -> dict:
        logging.debug("Запрос show_marks пользователем {message.from_.id}")


class Controller(AbstractController):
    def __init__(self, api: AbstractApi, db: AbstractDb, template_engine: AbstractTemplateEngine, markups: AbstractMarkups) -> None:
        super().__init__(api, db, template_engine, markups)
        self.__db: AbstractDb = db
        self.__template_engine: AbstractTemplateEngine = template_engine
        self.__api: AbstractApi = api
        self.__markups: AbstractMarkups = markups

    def start(self, message: Message) -> dict:
        if self.__db.user_in_table(message.from_.id):
            ans_message: str = self.__template_engine.render("registered.tfb")
            markup: str = self.__markups.all()
            return self.__base_ans(message.from_.id, ans_message, markup)
        markup: str = self.__markups.registration()
        return self.__unregistered(message.from_.id, markup)

    def help(self, message: Message) -> dict:
        ans_message: str = self.__template_engine.render("help.tfb")
        return self.__base_ans(message.from_.id, ans_message)

    def change_cerate_data(self, message: Message) -> dict:
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
        if self.__db.user_in_table(message.from_.id):
            data: dict = self.__db.get_user_data(message.from_.id)
            ans_message: str = self.__template_engine.render("user_data.tfd", data)
            return self.__base_ans(message.from_.id, ans_message)
        markup: str = self.__markups.change_data
        return self.__unregistered(message.from_.id, markup)

    def show_marks(self, message: Message) -> dict:
        if self.__db.user_in_table(message.from_.id):
            data: dict = self.__db.get_user_data(message.from_.id)
            response: dict | bool = self.__api.get_marks(data)
            if not response:
                return self.__unregistered(message.from_.id)

            ans_message: str = self.__template_engine.render("show_marks.tfb", response)
            return self.__base_ans(message.from_.id, ans_message)
        return self.__unregistered(message.from_.id)

    def __unregistered(self, user_id: str, markup: str = None) -> dict:
        return self.__base_ans(user_id, self.__template_engine.render("unregistered.tfb"), markup)

    @staticmethod
    def __base_ans(user_id: str, message: str, markup: str = None) -> dict:
        return {"user_id": user_id, "messages": [message], "markup": markup}
