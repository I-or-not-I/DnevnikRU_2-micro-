"""
Модуль моделей данных для Telegram API.

Модели основаны на Pydantic для валидации данных Telegram-сообщений.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class From(BaseModel):
    """Модель отправителя сообщения.

    :param id: Уникальный идентификатор пользователя
    :param is_bot: Флаг бота
    :param first_name: Имя пользователя
    :param last_name: Фамилия пользователя (опционально)
    :param username: Логин в Telegram
    :param language_code: Код языка
    """

    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: str
    language_code: str


class Chat(BaseModel):
    """Модель чата/диалога.

    :param id: ID чата
    :param first_name: Имя чата
    :param last_name: Фамилия чата (опционально)
    :param username: Логин чата
    :param type: Тип чата
    """

    id: int
    first_name: str
    last_name: Optional[str] = None
    username: str
    type: str


class Entity(BaseModel):
    """Модель текстовой сущности в сообщении.

    :param offset: Смещение начала сущности в тексте
    :param length: Длина сущности
    :param type: Тип сущности
    """

    offset: int
    length: int
    type: str


class Message(BaseModel):
    """Основная модель входящего сообщения Telegram.

    :param message_id: Уникальный идентификатор сообщения
    :param from_: Информация об отправителе (используйте alias "from")
    :param chat: Информация о чате
    :param date: Временная метка сообщения
    :param text: Текст сообщения
    :param entities: Список текстовых сущностей (опционально)
    :param login: Логин пользователя (опционально)
    :param password: Пароль пользователя (опционально)

    .. note::
        Для обработки зарезервированного слова 'from' используется alias 'from_'
    """

    message_id: int
    from_: From = Field(..., alias="from")
    chat: Chat
    date: int
    text: str
    entities: Optional[List[Entity]] = None
    login: Optional[str] = None
    password: Optional[str] = None
