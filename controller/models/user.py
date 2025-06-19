"""
Модуль моделей данных пользователей.

Модели основаны на SQLAlchemy.
"""

from sqlalchemy import JSON, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    id: Mapped[Integer] = mapped_column("id", Integer, primary_key=True)
    password: Mapped[Text] = mapped_column("password", type_=Text)
    login: Mapped[Text] = mapped_column("login", type_=Text)
    person_id: Mapped[Text] = mapped_column("person_id", type_=Text)
    school_id: Mapped[Text] = mapped_column("school_id", type_=Text)
    group_id: Mapped[Text] = mapped_column("group_id", type_=Text)
    cookies: Mapped[JSON] = mapped_column("cookies", type_=JSON)

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
