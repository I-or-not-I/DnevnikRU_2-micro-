import logging
import abc
import requests
import json
from telebot import types


class AbstractApi(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        logging.debug(f"Инициализация апи")

    @abc.abstractmethod
    def start(self, message: types.Message) -> dict:
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: start")

    @abc.abstractmethod
    def text_messages(self, message: types.Message) -> dict:
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: text_messages")

    @abc.abstractmethod
    def help(self, message: types.Message) -> dict:
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: help")

    @abc.abstractmethod
    def change_cerate_data(self, message: types.Message, login: str, password: str) -> dict:
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: change_cerate_data")

    @abc.abstractmethod
    def show_data(self, message: types.Message) -> dict:
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: show_data")

    @abc.abstractmethod
    def show_marks(self, message: types.Message) -> dict:
        logging.info(f"Пользователь: {message.from_user.id}. Вызвал функцию: show_marks")


class Api(AbstractApi):
    def __init__(self, controller_ip: str) -> None:
        super().__init__()
        self.__controller_ip: str = controller_ip

    def __get_data(self, path: str, message: types.Message, data: dict = None) -> dict:
        try:
            response: requests.Response = requests.post(
                f"{self.__controller_ip}/{path}",
                data=self.__dict_to_json(data) if data else self.__dict_to_json(message.json),
            )
        except requests.exceptions.ConnectionError:
            return self.__error_message(message)

        return response.json()

    def start(self, message: types.Message) -> dict:
        super().start(message)
        path: str = "start"
        return self.__get_data(path, message)

    def text_messages(self, message: types.Message) -> dict:
        super().text_messages(message)
        path: str = "text_messages"
        return self.__get_data(path, message)

    def help(self, message: types.Message) -> dict:
        super().help(message)
        path: str = "help"
        return self.__get_data(path, message)

    def change_cerate_data(self, message: types.Message, login: str, password: str) -> dict:
        super().change_cerate_data(message)
        path: str = "change_cerate_data"
        data: dict = self.__dict_to_json(message.json)
        data["login"] = login
        data["password"] = password
        return self.__get_data(path, message, data)

    def show_data(self, message: types.Message) -> dict:
        super().show_data(message)
        path: str = "show_data"
        return self.__get_data(path, message)

    def show_marks(self, message: types.Message) -> dict:
        super().show_marks(message)
        path: str = "show_marks"
        return self.__get_data(path, message)

    @staticmethod
    def __error_message(message: types.Message) -> dict:
        return {"user_id": message.from_user.id, "messages": ["Проблемы с сервером, попробуйте позже"], "markup": None}

    @staticmethod
    def __dict_to_json(data: dict) -> dict:
        return json.dumps(data, ensure_ascii=False)
