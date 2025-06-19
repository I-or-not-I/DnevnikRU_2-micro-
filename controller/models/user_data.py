"""
Модуль определяет модель данных пользователя для системы электронного дневника.

Модель UserData основана на Pydantic BaseModel и предоставляет:
- Валидацию данных пользователя
- Конвертацию данных из различных источников (ORM-режим)
- Автоматическую обработку строковых полей
- Поддержку псевдонимов (alias) для полей

Основные компоненты:
    UserData: Модель данных пользователя с полями для идентификации, аутентификации и сессии.
"""

from pydantic import BaseModel, ConfigDict, Field, JsonValue
from typing import Optional


class UserData(BaseModel):
    """
    Модель данных пользователя системы дневника.

    :param id: Уникальный числовой идентификатор пользователя в системе
    :type id: int
    :param password: Пароль от дневника, defaults to None
    :type password: Optional[str]
    :param login: Логин от дневника, defaults to None
    :type login: Optional[str]
    :param person_id: Идентификатор пользователя от дневника, defaults to None
    :type person_id: Optional[str]
    :param school_id: Идентификатор учебного заведения, defaults to None
    :type school_id: Optional[str]
    :param group_id: Идентификатор учебной группы/класса, defaults to None
    :type group_id: Optional[str]
    :param cookies: Данные сессии в JSON-формате, defaults to None
    :type cookies: Optional[JsonValue]
    :returns: Экземпляр модели UserData
    :rtype: UserData

    .. note::
        Конфигурация модели:
        - from_attributes=True: Разрешает создание из атрибутов объектов (ORM-режим)
        - populate_by_name=True: Разрешает использование как имен полей, так и alias
        - str_strip_whitespace=True: Автоматически удаляет пробелы по краям строк
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, str_strip_whitespace=True)

    id: int = Field(
        alias="id",
        description="Уникальный числовой идентификатор пользователя в системе",
    )

    password: Optional[str] = Field(
        default=None,
        alias="password",
        description="Пароль от дневника",
    )

    login: Optional[str] = Field(
        default=None,
        alias="login",
        description="Логин от дневника",
    )

    person_id: Optional[str] = Field(
        default=None,
        alias="person_id",
        description="Идентификатор пользователя от дневника",
    )

    school_id: Optional[str] = Field(
        default=None,
        alias="school_id",
        description="Идентификатор учебного заведения",
    )

    group_id: Optional[str] = Field(
        default=None,
        alias="group_id",
        description="Идентификатор учебной группы/класса",
    )

    cookies: Optional[JsonValue] = Field(
        default=None,
        alias="cookies",
        description="Данные сессии в JSON-формате",
    )
