"""
Модуль для работы с базой данных.
"""

import abc
from typing import Any, Callable
from psycopg2 import connect
from psycopg2.extensions import cursor


class AbstractDb(abc.ABC):
    """Абстрактный базовый класс для работы с базой данных.

    .. method:: create_data_table(cursor)
        :abstractmethod:

    .. method:: create_new_user(id, data, cursor)
        :abstractmethod:

    .. method:: update_user_data(id, data, cursor)
        :abstractmethod:

    .. method:: user_in_table(id, cursor)
        :abstractmethod:

    .. method:: get_user_data(id, cursor)
        :abstractmethod:
    """

    @abc.abstractmethod
    def __init__(self, data_path: str) -> None:
        """Инициализация подключения к БД.

        :param data_path: Параметры подключения к БД
        :type data_path: dict
        """

    @abc.abstractmethod
    def create_data_table(self, cursor: cursor = None) -> None:
        """Создание таблицы данных если не существует.

        :param cursor: Курсор для выполнения в транзакции (опционально)
        :type cursor: :class:`cursor`, optional
        """

    @abc.abstractmethod
    def create_new_user(self, id: int, data: dict, cursor: cursor = None) -> None:
        """Создание нового пользователя.

        :param id: Уникальный ID пользователя
        :param data: Данные пользователя
        :param cursor: Курсор для выполнения в транзакции (опционально)
        :type id: int
        :type data: dict
        :type cursor: :class:`cursor`, optional
        """

    @abc.abstractmethod
    def update_user_data(self, id: int, data: dict, cursor: cursor = None) -> None:
        """Обновление данных пользователя.

        :param id: ID пользователя для обновления
        :param data: Новые данные
        :param cursor: Курсор для выполнения в транзакции (опционально)
        :type id: int
        :type data: dict
        :type cursor: :class:`cursor`, optional
        """

    @abc.abstractmethod
    def user_in_table(self, id: int, cursor: cursor = None) -> bool:
        """Проверка существования пользователя.

        :param id: ID пользователя для проверки
        :param cursor: Курсор для выполнения в транзакции (опционально)
        :return: Флаг существования пользователя
        :rtype: bool
        """

    @abc.abstractmethod
    def get_user_data(self, id: int, cursor: cursor = None) -> dict:
        """Получение всех данных пользователя.

        :param id: ID пользователя
        :param cursor: Курсор для выполнения в транзакции (опционально)
        :return: Словарь с данными пользователя
        :rtype: dict
        """

class Db(AbstractDb):
    """Конкретная реализация работы с PostgreSQL.

    :param db_data: Конфигурация подключения к БД
    :type db_data: dict

    .. note::
        Структура таблицы данных:
        - id: INTEGER
        - password: TEXT
        - login: TEXT
        - person_id: TEXT
        - school_id: TEXT
        - group_id: TEXT
        - cookies: JSON
    """

    def __init__(self, db_data: dict) -> None:
        self.__db_data: dict = db_data
        self.__columns: dict = {
            "id": "INTEGER",
            "password": "TEXT",
            "login": "TEXT",
            "person_id": "TEXT",
            "school_id": "TEXT",
            "group_id": "TEXT",
            "cookies": "JSON",
        }

    def __connection(self, func: Callable, id: int = None, data: dict = None, commit: bool = False) -> Any:
        """Менеджер подключений и транзакций.

        :meta private:
        :param func: Функция для выполнения
        :param id: ID пользователя (опционально)
        :param data: Данные пользователя (опционально)
        :param commit: Флаг необходимости коммита
        :return: Результат выполнения функции
        """
        with connect(**self.__db_data) as connection:
            with connection.cursor() as cursor:
                ans: Any = func(cursor=cursor, **{k: v for k, v in {"id": id, "data": data}.items() if v is not None})
                if commit:
                    connection.commit()
                return ans

    def create_data_table(self, cursor: cursor = None) -> None:
        """Создает таблицу данных если она не существует."""
        if not cursor:
            return self.__connection(self.create_data_table, commit=True)
        enquiry: str = f"CREATE TABLE IF NOT EXISTS data ({', '.join(f'{k} {v}' for k, v in self.__columns.items())})"
        cursor.execute(enquiry)

    def create_new_user(self, id: int, data: dict, cursor: cursor = None) -> None:
        """Добавляет нового пользователя в БД."""
        if not cursor:
            return self.__connection(func=self.create_new_user, id=id, data=data, commit=True)
        data["id"] = id
        enquiry: str = "INSERT INTO data (%s) VALUES (%s)" % (", ".join(data.keys()), ", ".join(["%s"] * len(data)))
        cursor.execute(enquiry, list(data.values()))

    def update_user_data(self, id: int, data: dict, cursor: cursor = None) -> None:
        """Обновляет данные существующего пользователя."""
        if not cursor:
            return self.__connection(func=self.update_user_data, id=id, data=data, commit=True)
        cursor.execute(f"UPDATE data SET {', '.join(f"{k} = '{v}'" for k, v in data.items())} WHERE id = {id}")

    def user_in_table(self, id: int, cursor: cursor = None) -> bool:
        """Проверяет наличие пользователя в БД."""
        if not cursor:
            return self.__connection(func=self.user_in_table, id=id)
        cursor.execute(f"SELECT id FROM data WHERE id = '{id}'")
        return cursor.fetchone() is not None

    def get_user_data(self, id: int, cursor: cursor = None) -> dict:
        """Возвращает все данные пользователя в виде словаря."""
        if not cursor:
            return self.__connection(func=self.get_user_data, id=id)
        cursor.execute(f"SELECT {', '.join(self.__columns.keys())} FROM data WHERE id = {id}")
        return dict(zip(self.__columns.keys(), cursor.fetchone()))
