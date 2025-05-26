"""
Модуль для генерации клавиатурных разметок Telegram бота.
"""

import abc
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


class AbstractMarkups(abc.ABC):
    """Абстрактный базовый класс для генерации клавиатурных разметок.

    .. method:: registration()
        :abstractmethod:

    .. method:: change_data()
        :abstractmethod:

    .. method:: all()
        :abstractmethod:
    """

    @abc.abstractmethod
    def registration(self) -> str:
        """Генерация разметки для этапа регистрации.

        :return: JSON-строка с клавиатурой
        :rtype: str
        """

    @abc.abstractmethod
    def change_data(self) -> str:
        """Генерация разметки для изменения данных.

        :return: JSON-строка с клавиатурой
        :rtype: str
        """

    @abc.abstractmethod
    def all(self) -> str:
        """Генерация полной разметки с основными функциями.

        :return: JSON-строка с клавиатурой
        :rtype: str
        """


class Markups(AbstractMarkups):
    """Конкретная реализация генератора клавиатурных разметок."""

    def registration(self) -> str:
        """Создает клавиатуру для начальной регистрации.

        Кнопки:
        - "Начать регистрацию"
        - "Помощь"

        :return: JSON-строка клавиатуры 2x1
        """
        buttons: tuple = ("Начать регистрацию", "Помощь")
        return self.__default_markup(buttons, row_width=1)

    def change_data(self) -> str:
        """Создает клавиатуру для изменения данных.

        Кнопки:
        - "Изменить данные"
        - "Помощь"

        :return: JSON-строка клавиатуры 2x1
        """
        buttons: tuple = ("Изменить данные", "Помощь")
        return self.__default_markup(buttons, row_width=1)

    def all(self) -> str:
        """Создает основную клавиатуру со всеми функциями.

        Кнопки:
        - "Оценки"
        - "Расписание"
        - "Изменить данные"
        - "Помощь"

        :return: JSON-строка клавиатуры 2x2
        """
        buttons: tuple = ("Оценки", "Расписание", "Изменить данные", "Помощь")
        return self.__default_markup(buttons, row_width=2)

    @staticmethod
    def __default_markup(buttons: tuple, row_width: int = 2) -> str:
        """Приватный метод создания базовой клавиатуры.

        :param buttons: Кортеж с текстами кнопок
        :param row_width: Количество кнопок в ряду
        :return: JSON-представление клавиатуры
        :rtype: str
        :meta private:
        """
        markup: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
        markup.add(*(KeyboardButton(button) for button in buttons))
        return markup.to_json()
