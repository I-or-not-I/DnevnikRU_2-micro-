"""
Модуль для генерации клавиатурных разметок Telegram бота.

Предоставляет:
- Абстрактный интерфейс для создания клавиатур
- Конкретные реализации клавиатур для разных сценариев
- Генерацию JSON-представления клавиатур для Telegram API

Основные функции:
- Создание клавиатуры для регистрации
- Создание клавиатуры для изменения данных
- Создание основной клавиатуры со всеми функциями

Компоненты:
    AbstractMarkups: Абстрактный интерфейс генератора разметок
    Markups: Конкретная реализация генератора

.. note::
    Все методы возвращают JSON-строки, готовые к отправке в Telegram API.
    Разметки создаются с помощью telebot.types.ReplyKeyboardMarkup.
"""

import abc
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


class AbstractMarkups(abc.ABC):
    """
    Абстрактный базовый класс для генерации клавиатурных разметок.

    Определяет обязательные методы для создания:
    - Клавиатуры регистрации
    - Клавиатуры изменения данных
    - Основной клавиатуры
    """

    @abc.abstractmethod
    def registration(self) -> str:
        """
        Абстрактный метод генерации разметки для этапа регистрации.

        :return: JSON-строка с клавиатурой
        :rtype: str
        :meta abstract:
        """

    @abc.abstractmethod
    def change_data(self) -> str:
        """
        Абстрактный метод генерации разметки для изменения данных.

        :return: JSON-строка с клавиатурой
        :rtype: str
        :meta abstract:
        """

    @abc.abstractmethod
    def all(self) -> str:
        """
        Абстрактный метод генерации полной разметки с основными функциями.

        :return: JSON-строка с клавиатурой
        :rtype: str
        :meta abstract:
        """


class Markups(AbstractMarkups):
    """
    Конкретная реализация генератора клавиатурных разметок.

    :returns: Инициализированный экземпляр генератора разметок
    :rtype: Markups
    """

    def registration(self) -> str:
        """
        Создает клавиатуру для начальной регистрации.

        Кнопки:
        - "Начать регистрацию"
        - "Помощь"

        :return: JSON-строка клавиатуры 2x1
        :rtype: str
        """
        buttons: tuple = ("Начать регистрацию", "Помощь")
        return self.__default_markup(buttons, row_width=1)

    def change_data(self) -> str:
        """
        Создает клавиатуру для изменения данных пользователя.

        Кнопки:
        - "Изменить данные"
        - "Помощь"

        :return: JSON-строка клавиатуры 2x1
        :rtype: str
        """
        buttons: tuple = ("Изменить данные", "Помощь")
        return self.__default_markup(buttons, row_width=1)

    def all(self) -> str:
        """
        Создает основную клавиатуру со всеми функциями бота.

        Кнопки:
        - "Оценки"
        - "Расписание"
        - "Изменить данные"
        - "Помощь"

        :return: JSON-строка клавиатуры 2x2
        :rtype: str
        """
        buttons: tuple = ("Оценки", "Расписание", "Изменить данные", "Помощь")
        return self.__default_markup(buttons, row_width=2)

    @staticmethod
    def __default_markup(buttons: tuple, row_width: int = 2) -> str:
        """
        Приватный метод создания базовой клавиатуры.

        :param buttons: Кортеж с текстами кнопок
        :param row_width: Количество кнопок в ряду
        :type buttons: tuple
        :type row_width: int
        :return: JSON-представление клавиатуры
        :rtype: str
        :meta private:
        """
        markup: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
        markup.add(*(KeyboardButton(button) for button in buttons))
        return markup.to_json()
