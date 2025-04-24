import abc
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


class AbstractMarkups(abc.ABC):
    @abc.abstractmethod
    def registration(self) -> str:
        pass

    @abc.abstractmethod
    def change_data(self) -> str:
        pass

    @abc.abstractmethod
    def all(self) -> str:
        pass


class Markups(AbstractMarkups):
    def registration(self) -> str:
        buttons: tuple = ("Начать регистрацию", "Помощь")
        return self.__default_markup(buttons)

    def change_data(self) -> str:
        buttons: tuple = ("Изменить данные", "Помощь")
        return self.__default_markup(buttons)

    def all(self) -> str:
        buttons: tuple = ("Оценки", "Изменить данные", "Помощь")
        return self.__default_markup(buttons)

    @staticmethod
    def __default_markup(buttons: tuple, row_width: int = 2) -> str:
        markup: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
        markup.add(*(KeyboardButton(button) for button in buttons))
        return markup.to_json()
