"""
Асинхронный модуль для работы с PostgreSQL через SQLAlchemy.

Предоставляет:
- Абстрактный интерфейс для работы с БД
- Конкретную реализацию на базе SQLAlchemy Core
- Операции CRUD для модели пользователя

.. note::
    Зависимости:
    - SQLAlchemy: Для ORM и работы с базами данных
    - asyncpg: Асинхронный драйвер PostgreSQL

Основные компоненты:
    AbstractDb: Абстрактный интерфейс базы данных
    Database: Конкретная реализация для PostgreSQL
"""

from abc import ABC, abstractmethod
from logging import error
from typing import Any, Optional, Callable
from sqlalchemy import Result, Select, Update, update, exists, select, exc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.exc import SQLAlchemyError

from models.user import Base, User
from models.user_data import UserData


class AbstractDb(ABC):
    """
    Абстрактный интерфейс для работы с базой данных.

    Определяет обязательные методы для:
    - Создания таблиц
    - Создания/обновления пользователей
    - Проверки существования пользователей
    - Получения данных пользователей
    """

    @abstractmethod
    def __init__(self, db_config: dict) -> None:
        """
        Абстрактный конструктор базы данных.

        :param db_config: Конфигурация подключения к БД
        :type db_config: dict
        :meta abstract:
        """

    @abstractmethod
    async def create_tables(self) -> None:
        """
        Абстрактный метод создания таблиц.

        :meta abstract:
        """
        pass

    @abstractmethod
    async def create_update_user(self, data: UserData) -> bool:
        """
        Абстрактный метод создания/обновления пользователя.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Статус операции (True - успех, False - неудача)
        :rtype: bool
        :meta abstract:
        """
        pass

    @abstractmethod
    async def user_exists(self, data: UserData) -> bool:
        """
        Абстрактный метод проверки существования пользователя.

        :param data: Данные пользователя для проверки
        :type data: UserData
        :returns: Флаг существования пользователя
        :rtype: bool
        :meta abstract:
        """
        pass

    @abstractmethod
    async def get_user(self, data: UserData) -> Optional[User]:
        """
        Абстрактный метод получения пользователя.

        :param data: Данные пользователя для поиска
        :type data: UserData
        :returns: Найденный пользователь или None
        :rtype: Optional[User]
        :meta abstract:
        """
        pass


class Database(AbstractDb):
    """
    Реализация работы с PostgreSQL через SQLAlchemy Core.

    :param db_config: Конфигурация подключения к БД
        - user: Имя пользователя
        - password: Пароль
        - host: Хост БД
        - port: Порт БД
        - database: Имя базы данных
    :type db_config: dict
    :returns: Инициализированный экземпляр Database
    :rtype: Database
    """

    def __init__(self, db_config: dict) -> None:
        self.engine: AsyncEngine = create_async_engine(
            f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}",
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
        )

        self.session_factory = async_sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    async def create_tables(self) -> None:
        """
        Создает все таблицы в базе данных.

        Использует метаданные из Base.metadata.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def __execute(self, operation: Callable, must_commit: bool = False) -> Any:
        """
        Приватный метод выполнения операций с БД.

        :param operation: Функция-операция для выполнения
        :param must_commit: Требуется ли коммит после операции
        :type operation: Callable
        :type must_commit: bool
        :returns: Результат операции
        :rtype: Any
        :raises:
            - SQLAlchemyError: При ошибках работы с БД
        :meta private:
        """
        session: AsyncSession = self.session_factory()

        try:
            result: Any = await operation(session)
            if must_commit:
                await session.commit()
            return result
        except exc.SQLAlchemyError as e:
            await session.rollback()
            error("Database error: %s", e)
        finally:
            await session.close()

    async def create_update_user(self, data: UserData) -> bool:
        """
        Создает или обновляет пользователя в базе данных.

        :param data: Данные пользователя
        :type data: UserData
        :returns: Статус операции (True - успех, False - неудача)
        :rtype: bool
        """

        async def _create_operation(sess: AsyncSession) -> bool:
            """Внутренняя функция создания пользователя."""
            try:
                user = User(**data.model_dump())
                sess.add(user)
                await sess.flush()
                return True
            except SQLAlchemyError:
                await sess.rollback()
                return False

        async def _update_operation(sess: AsyncSession) -> bool:
            """Внутренняя функция обновления пользователя."""
            try:
                stmt: Update = (
                    update(User)
                    .where(User.id == data.id)
                    .values(**data.model_dump())
                    .execution_options(synchronize_session="fetch")
                )
                await sess.execute(stmt)
                return True
            except SQLAlchemyError:
                await sess.rollback()
                return False

        if not await self.user_exists(data):
            return await self.__execute(_create_operation, True)
        else:
            return await self.__execute(_update_operation, True)

    async def user_exists(self, data: UserData) -> bool:
        """
        Проверяет существование пользователя в базе.

        :param data: Данные пользователя для проверки
        :type data: UserData
        :returns: Флаг существования пользователя
        :rtype: bool
        """

        async def _operation(sess: AsyncSession) -> bool:
            query: Select = select(exists().where(User.id == data.id))
            result: Result = await sess.execute(query)
            return result.scalar() is True

        return await self.__execute(_operation)

    async def get_user(self, data: UserData) -> Optional[User]:
        """
        Получает пользователя по идентификатору.

        :param data: Данные пользователя для поиска
        :type data: UserData
        :returns: Найденный пользователь или None
        :rtype: Optional[User]
        """

        async def _operation(sess: AsyncSession) -> Optional[User]:
            query: Select = select(User).where(User.id == data.id)
            result: Result = await sess.execute(query)
            return result.scalar_one_or_none()

        return await self.__execute(_operation)
