"""
Модуль моделей данных пользователей.

Модели основаны на SQLAlchemy.
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa


class Base(DeclarativeBase):
    """Базовый декларативный класс для моделей SQLAlchemy."""


class User(Base):
    """Модель для представления пользователя в базе данных.

    Соответствует таблице ``data`` и содержит следующие колонки:

    :param id: Уникальный идентификатор пользователя
    :type id: :class:`sqlalchemy.Integer`
    :param password: Пароль пользователя
    :type password: :class:`sqlalchemy.Text`
    :param login: Логин пользователя
    :type login: :class:`sqlalchemy.Text`
    :param person_id: Идентификатор личности
    :type person_id: :class:`sqlalchemy.Text`
    :param school_id: Идентификатор учебного заведения
    :type school_id: :class:`sqlalchemy.Text`
    :param group_id: Идентификатор группы/класса
    :type group_id: :class:`sqlalchemy.Text`
    :param cookies: Куки пользователя
    :type cookies: :class:`sqlalchemy.dialects.postgresql.JSONB`
    """

    __tablename__: str = "data"

    id: sa.Column = sa.Column(sa.Integer, primary_key=True)
    password: sa.Column = sa.Column(sa.Text)
    login: sa.Column = sa.Column(sa.Text)
    person_id: sa.Column = sa.Column(sa.Text)
    school_id: sa.Column = sa.Column(sa.Text)
    group_id: sa.Column = sa.Column(sa.Text)
    cookies: sa.Column = sa.Column(JSONB)

    def to_dict(self) -> dict:
        """Преобразует объект User в словарь для сериализации в JSON.

        :return: Словарь с основными атрибутами пользователя
        :rtype: dict

        .. warning::
            При изменении состава полей модели необходимо обновлять этот метод
        """
        return {
            "id": self.id,
            "login": self.login,
            "password": self.password,
            "person_id": self.person_id,
            "school_id": self.school_id,
            "group_id": self.group_id,
            "cookies": self.cookies,
        }
