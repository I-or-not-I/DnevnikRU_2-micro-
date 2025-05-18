"""
Модуль с моделью данных пользователя.
"""

from pydantic import BaseModel, Json


class UserData(BaseModel):
    """Модель данных пользователя.

    :param id: Уникальный идентификатор пользователя (опционально)
    :param password: Пароль пользователя (обязательный)
    :param login: Логин пользователя (обязательный)
    :param person_id: Идентификатор личности в системе (опционально)
    :param school_id: Идентификатор учебного заведения (опционально)
    :param group_id: Идентификатор класса (опционально)
    :param cookies: Куки сессии (опционально)
    """

    id: int | None = None
    password: str
    login: str
    person_id: str | None = None
    school_id: str | None = None
    group_id: str | None = None
    cookies: Json | None = None
