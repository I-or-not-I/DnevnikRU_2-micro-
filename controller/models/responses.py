"""
Модуль определяет Pydantic-модели для обработки различных структур API-ответов.

.. note::
   Все поля необязательные со значениями по умолчанию ``None``.

:classes:
    - GetMarks: Модель данных об учебных оценках
    - GetTimetable: Модель данных расписания
    - UserExists: Модель проверки существования пользователя
    - ChangeCreateData: Модель статуса операции
"""

from pydantic import BaseModel
from typing import Optional


class GetMarks(BaseModel):
    """
    Модель-контейнер для данных об учебных оценках.

    :param marks: Словарь соответствия предметов спискам оценок
    :type marks: Optional[dict[str, list[int]]]
    :returns: Экземпляр модели GetMarks
    :rtype: GetMarks
    """

    marks: Optional[dict[str, list[int]]] = None


class GetTimetable(BaseModel):
    """
    Модель-контейнер для данных расписания.

    :param timetable: Строковое представление расписания
    :type timetable: Optional[str]
    :returns: Экземпляр модели GetTimetable
    :rtype: GetTimetable
    """

    timetable: Optional[str] = None


class UserExists(BaseModel):
    """
    Модель ответа для проверки существования пользователя.

    :param user_exists: Флаг существования пользователя
    :type user_exists: Optional[bool]
    :returns: Экземпляр модели UserExists
    :rtype: UserExists
    """

    user_exists: Optional[bool] = None


class ChangeCreateData(BaseModel):
    """
    Модель статуса операции для запросов на создание/изменение.

    :param success: Флаг успешности операции
    :type success: Optional[bool]
    :returns: Экземпляр модели ChangeCreateData
    :rtype: ChangeCreateData
    """

    success: Optional[bool] = None
