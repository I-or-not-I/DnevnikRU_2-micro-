import logging
import abc
from telebot import TeleBot, types

from src.api import AbstractApi


class AbstractTgBot(abc.ABC):
    @abc.abstractmethod
    def __init__(self, token: str) -> None:
        logging.debug("Инициализация бота")

    @abc.abstractmethod
    def run(self) -> None:
        logging.info("Запуск бота")


class TgBot(TeleBot, AbstractTgBot):
    def __init__(self, token: str, api: AbstractApi) -> None:
        super().__init__(token)
        self.__api: AbstractApi = api

    def run(self) -> None:
        super().run()
        self.register_message_handler(self.__start, commands=["start"])
        self.register_message_handler(self.__help, commands=["help"])
        self.register_message_handler(self.__show_data, commands=["show_data"])
        self.register_message_handler(self.__change_cerate_data, commands=["change_data"])
        self.register_message_handler(self.__show_marks, commands=["grades"])

        self.register_message_handler(self.__text_messages, content_types=["text"])

        self.polling(non_stop=True)

    def __start(self, message: types.Message) -> None:
        data: dict = self.__api.start(message)
        self.__send_data(data)

    def __text_messages(self, message: types.Message) -> None:
        data: dict = self.__api.text_messages(message)
        self.__send_data(data)

    def __help(self, message: types.Message) -> None:
        data: dict = self.__api.help(message)
        self.__send_data(data)

    def __change_cerate_data(self, message: types.Message, login: str = None, password: str = None) -> None:
        if login is None or password is None:
            self.send_message(message.from_user.id, "Введите логин:")
            self.register_next_step_handler(message, self.__get_login)
            return

        data: dict = self.__api.change_cerate_data(message, login, password)
        self.__send_data(data)

    def __get_login(self, message: types.Message) -> None:
        login: str = message.text.strip()
        self.send_message(message.from_user.id, "Введите пароль:")
        self.register_next_step_handler(message, self.__get_password, login)

    def __get_password(self, message: types.Message, login: str) -> None:
        password: str = message.text.strip()
        self.__change_cerate_data(message, login, password)

    def __show_data(self, message: types.Message) -> None:
        data: dict = self.__api.show_data(message)
        self.__send_data(data)

    def __show_marks(self, message: types.Message) -> None:
        data: dict = self.__api.show_marks(message)
        self.__send_data(data)

    def __send_data(self, data: dict) -> None:
        for message in data["messages"]:
            self.send_message(data["user_id"], message, reply_markup=data["markup"])
