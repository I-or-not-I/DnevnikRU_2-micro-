"""
Модуль определяет модели ответов API для образовательных данных.

Модели:
    GetMarks: Модель ответа с оценками пользователя
    GetTimetable: Модель ответа с расписанием занятий

.. note::
    Все поля необязательные со значением по умолчанию None.
"""

from pydantic import BaseModel
from typing import Optional


class GetMarks(BaseModel):
    """
    Модель ответа, содержащая оценки пользователя.

    :param marks: Словарь с оценками по предметам
        - Ключи: названия предметов (str)
        - Значения: списки оценок (list)
    :type marks: Optional[dict[str, list]]
    :returns: Экземпляр модели GetMarks
    :rtype: GetMarks
    """
    marks: Optional[dict[str, list]] = None


class GetTimetable(BaseModel):
    """
    Модель ответа, содержащая расписание занятий.

    :param timetable: Строковое представление расписания
        - Может быть в формате JSON, HTML или plain text
    :type timetable: Optional[str]
    :returns: Экземпляр модели GetTimetable
    :rtype: GetTimetable
    """
    timetable: Optional[str] = None