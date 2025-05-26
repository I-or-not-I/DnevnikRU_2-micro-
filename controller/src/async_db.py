"""
Асинхронный модуль для работы с PostgreSQL через SQLAlchemy.

.. note::
    Зависимости:
    - SQLAlchemy: Для ORM и работы с базами данных
    - asyncpg: Асинхронный драйвер PostgreSQL
"""

from abc import ABC, abstractmethod
from logging import error
from typing import Any, Optional, Callable
from sqlalchemy import CursorResult, Result, Select, Update, update, exists, select, exc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from models.user import Base, User


class AbstractDb(ABC):
    """Абстрактный базовый класс для работы с базой данных.

    :param db_config: Конфигурация подключения к БД
    :type db_config: dict
    """

    @abstractmethod
    def __init__(self, db_config: dict) -> None:
        """Инициализация абстрактного класса БД."""

    @abstractmethod
    async def create_tables(self) -> None:
        """Создает все таблицы в базе данных из метаданных Base."""

    @abstractmethod
    async def create_user(self, user_id: int, data: dict) -> None:
        """Создает новую запись пользователя.

        :param user_id: Уникальный идентификатор пользователя Telegram
        :type user_id: int
        :param data: Данные пользователя для сохранения
        :type data: dict
        """

    @abstractmethod
    async def update_user(self, user_id: int, data: dict) -> bool:
        """Обновляет данные пользователя.

        :param user_id: Идентификатор пользователя для обновления
        :type user_id: int
        :param data: Новые данные пользователя
        :type data: dict
        :return: Флаг успешного выполнения операции
        :rtype: bool
        """

    @abstractmethod
    async def user_exists(self, user_id: int) -> bool:
        """Проверяет существование пользователя в БД.

        :param user_id: Идентификатор пользователя для проверки
        :type user_id: int
        :return: Результат проверки существования
        :rtype: bool
        """

    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получает объект пользователя из БД.

        :param user_id: Идентификатор искомого пользователя
        :type user_id: int
        :return: Объект User или None если не найден
        :rtype: Optional[User]
        """


class Database(AbstractDb):
    """Реализация асинхронного взаимодействия с PostgreSQL.

    :param db_config: Конфигурация подключения к БД
    :type db_config: dict

    .. note::
        Пример конфигурации:
        {
            'user': 'username',
            'password': 'password',
            'host': 'localhost',
            'port': '5432',
            'database': 'dbname'
        }
    """

    def __init__(self, db_config: dict) -> None:
        """
        Инициализирует асинхронный движок и сессию.

        :param db_config: Параметры подключения к БД
        """
        self.engine: AsyncEngine = create_async_engine(
            f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}",
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
        )

        self.session_factory = async_sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

    async def create_tables(self) -> None:
        """Создает все таблицы из метаданных Base.

        .. note::
            Использует асинхронное выполнение через engine.begin()
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def __execute(self, operation: Callable, must_commit: bool = False) -> Any:
        """Внутренний метод для выполнения операций с БД.

        :param operation: Выполняемая операция
        :type operation: Callable
        :param must_commit: Флаг необходимости коммита
        :type must_commit: bool
        :return: Результат выполнения операции
        :raises exc.SQLAlchemyError: При ошибках работы с БД

        .. note::
            Автоматически управляет сессиями и транзакциями
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

    async def create_user(self, user_id: int, data: dict) -> None:
        """Создает новую запись пользователя в БД.

        :param user_id: Уникальный идентификатор пользователя
        :type user_id: int
        :param data: Данные для сохранения
        :type data: dict
        """

        async def _operation(sess: AsyncSession) -> User:
            user = User(id=user_id, **data)
            sess.add(user)
            await sess.flush()

        return await self.__execute(_operation, True)

    async def update_user(self, user_id: int, data: dict) -> bool:
        """Обновляет данные существующего пользователя.

        :param user_id: Идентификатор обновляемого пользователя
        :type user_id: int
        :param data: Новые данные для обновления
        :type data: dict
        :return: True если обновление прошло успешно
        :rtype: bool
        """

        async def _operation(sess: AsyncSession) -> bool:
            stmt: Update = (
                update(User).where(User.id == user_id).values(**data).execution_options(synchronize_session="fetch")
            )
            result: CursorResult = await sess.execute(stmt)
            return result.rowcount > 0

        return await self.__execute(_operation, True)

    async def user_exists(self, user_id: int) -> bool:
        """Проверяет наличие пользователя в базе данных.

        :param user_id: Идентификатор для проверки
        :type user_id: int
        :return: Результат проверки существования
        :rtype: bool
        """

        async def _operation(sess: AsyncSession) -> bool:
            query: Select = select(exists().where(User.id == user_id))
            result: Result = await sess.execute(query)
            return result.scalar()

        return await self.__execute(_operation)

    async def get_user(self, user_id: int) -> Optional[User]:
        """Возвращает полный объект пользователя.

        :param user_id: Идентификатор искомого пользователя
        :type user_id: int
        :return: Найденный пользователь или None
        :rtype: Optional[User]
        """

        async def _operation(sess: AsyncSession) -> Optional[User]:
            query: Select = select(User).where(User.id == user_id)
            result: Result = await sess.execute(query)
            return result.scalar_one_or_none()

        return await self.__execute(_operation)
