"""
Модуль телеграм-бота.
"""

import logging
import abc
from io import BytesIO
from telebot import TeleBot, types
from src.async_api import AbstractApi


class AbstractTgBot(abc.ABC):
    """Абстрактный базовый класс для телеграм-бота.

    :param token: Токен бота, полученный от BotFather
    :type token: str
    """

    @abc.abstractmethod
    def __init__(self, token: str) -> None:
        """Инициализация абстрактного бота"""

    @abc.abstractmethod
    def run(self) -> None:
        """Основной метод для запуска бота"""


class TgBot(TeleBot, AbstractTgBot):
    """Конкретная реализация телеграм-бота с интеграцией API.

    Наследует:
    - :class:`TeleBot` из python-telegram-bot
    - :class:`AbstractTgBot` из текущего модуля

    :param token: Токен бота
    :param api: Реализация AbstractApi для работы с бэкендом
    :type token: str
    :type api: :class:`AbstractApi`
    """

    def __init__(self, token: str, api: AbstractApi) -> None:
        """
        :raises ValueError: При невалидном токене
        """
        logging.debug("Инициализация бота")
        super().__init__(token)
        self.__api: AbstractApi = api

        self.__commands: dict = {
            "Начать регистрацию": self.__change_create_data,
            "Изменить данные": self.__change_create_data,
            "Мои данные": self.__show_data,
            "Оценки": self.__show_marks,
            "Расписание": self.__show_timetable,
            "Помощь": self.__help,
        }

    def run(self) -> None:
        """Запуск основного цикла работы бота.

        Регистрирует обработчики для:
        - Команд: /start, /help, /show_data, /change_data, /grades
        - Текстовых сообщений
        - Запускает бесконечный polling

        :raises ConnectionError: При проблемах с подключением
        """
        logging.info("Бот запущен")
        self.register_message_handler(self.__start, commands=["start"])
        self.register_message_handler(self.__help, commands=["help"])
        self.register_message_handler(self.__show_data, commands=["show_data"])
        self.register_message_handler(self.__change_create_data, commands=["change_data"])
        self.register_message_handler(self.__show_marks, commands=["grades"])
        self.register_message_handler(self.__show_timetable, commands=["timetable"])

        self.register_message_handler(self.__text_messages, content_types=["text"])

        self.polling(non_stop=True)

    def __start(self, message: types.Message) -> None:
        """Обработчик команды /start.

        :param message: Входящее сообщение
        :type message: :class:`types.Message`
        """
        data: dict = self.__api.start(message)
        self.__send_data(data)

    def __text_messages(self, message: types.Message) -> None:
        """Обработчик текстовых сообщений.

        :param message: Текстовое сообщение пользователя
        :type message: :class:`types.Message`
        """
        if message.text in self.__commands:
            self.__commands[message.text](message)
            return
        self.__send_data({"user_id": message.from_user.id, "messages": ["Неизвестная команда"], "markup": None})

    def __help(self, message: types.Message) -> None:
        """Обработчик команды /help.

        :param message: Входящее сообщение
        :type message: :class:`types.Message`
        """
        data: dict = self.__api.help(message)
        self.__send_data(data)

    def __change_create_data(self, message: types.Message, login: str = None, password: str = None) -> None:
        """Обработчик изменения учетных данных.

        :param message: Входящее сообщение
        :param login: Логин пользователя (опционально)
        :param password: Пароль пользователя (опционально)
        :type message: :class:`types.Message`
        :type login: :obj:`str`, optional
        :type password: :obj:`str`, optional

        .. note::
            Если логин/пароль не указаны, запускает цепочку запросов:
            1. Запрос логина
            2. Запрос пароля
        """
        if login is None or password is None:
            self.send_message(message.from_user.id, "Введите логин:")
            self.register_next_step_handler(message, self.__get_login)
            return

        data: dict = self.__api.change_create_data(message, login, password)
        self.__send_data(data)

    def __get_login(self, message: types.Message) -> None:
        """Получение логина от пользователя.

        :param message: Сообщение с логином
        :type message: :class:`types.Message`
        :meta private:
        """
        login: str = message.text.strip()
        self.send_message(message.from_user.id, "Введите пароль:")
        self.register_next_step_handler(message, self.__get_password, login)

    def __get_password(self, message: types.Message, login: str) -> None:
        """Получение пароля от пользователя.

        :param message: Сообщение с паролем
        :param login: Полученный ранее логин
        :type message: :class:`types.Message`
        :type login: :obj:`str`
        :meta private:
        """
        password: str = message.text.strip()
        self.__change_create_data(message, login, password)

    def __show_data(self, message: types.Message) -> None:
        """Показать данные пользователя.

        :param message: Входящее сообщение
        :type message: :class:`types.Message`
        """
        data: dict = self.__api.show_data(message)
        self.__send_data(data)

    def __show_marks(self, message: types.Message) -> None:
        """Показать оценки пользователя.

        :param message: Входящее сообщение
        :type message: :class:`types.Message`
        """
        data: dict = self.__api.show_marks(message)
        self.__send_data(data)

    def __show_timetable(self, message: types.Message) -> None:
        """Показать расписание пользователя.

        :param message: Входящее сообщение
        :type message: :class:`types.Message`
        """
        data: dict = self.__api.show_timetable(message)
        self.__send_file(data)

    def __send_data(self, data: dict) -> None:
        """Отправка данных пользователю.

        :param data: Словарь с данными для отправки
        :type data: :obj:`dict`

        .. note::
            Формат данных:
            - user_id: ID пользователя (int)
            - messages: Список сообщений (List[str])
            - markup: Разметка клавиатуры (Optional)

        :raises KeyError: При отсутствии обязательных ключей
        """
        for message in data["messages"]:
            self.send_message(data["user_id"], message, reply_markup=data["markup"])

    def __send_file(self, data: dict) -> None:
        """Отправка данных пользователю (файлом).

        :param data: Словарь с данными для отправки
        :type data: :obj:`dict`

        .. note::
            Формат данных:
            - user_id: ID пользователя (int)
            - message: Сообщение (str)
            - file_name: Имя файла (str)
            - markup: Разметка клавиатуры (Optional)

        :raises KeyError: При отсутствии обязательных ключей
        """
        file_buffer = BytesIO(data["message"].encode("utf-8"))
        self.send_document(
            chat_id=data["user_id"],
            document=file_buffer,
            visible_file_name=data["file_name"],
            reply_markup=data["markup"],
        )
