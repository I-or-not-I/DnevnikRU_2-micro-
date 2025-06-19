"""
Модуль с моделью данных пользователя.
"""

from pydantic import BaseModel, Json
from typing import Optional


class UserData(BaseModel):
    """Модель данных пользователя.

    :param id: Уникальный идентификатор пользователя
    :param password: Пароль пользователя (опционально)
    :param login: Логин пользователя (опционально)
    """

    id: int
    password: Optional[str] = None
    login: Optional[str] = None
