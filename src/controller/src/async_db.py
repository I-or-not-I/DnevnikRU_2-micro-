"""
Асинхронный модуль для работы с бд через SQLAlchemy
"""

from abc import ABC, abstractmethod
from logging import error
from typing import Any, Optional, Callable
from sqlalchemy import CursorResult, Result, Select, Update, update, exists, select, exc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from models.user import Base, User


class AbstractDb(ABC):
    """Абстрактный базовый класс базы данных.

    :param db_config: Словарь с данными для подключения к бд
    """

    @abstractmethod
    def __init__(self, db_config: dict) -> None:
        """Инициализация Abstract."""

    @abstractmethod
    async def create_tables(self) -> None:
        """Создает все таблицы в базе данных"""

    @abstractmethod
    async def create_user(self, user_id: int, data: dict) -> None:
        """Создает нового пользователя"""

    @abstractmethod
    async def update_user(self, user_id: int, data: dict) -> bool:
        """Обновляет данные пользователя, возвращает признак успеха"""

    @abstractmethod
    async def user_exists(self, user_id: int) -> bool:
        """Проверяет существование пользователя"""

    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[User]:
        """Возвращает объект User или None"""


class Database:
    """Асинхронная реализация работы с PostgreSQL"""

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
        """Создает все таблицы в базе данных"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def __execute(self, operation: Callable, must_commit: bool = False) -> Any:
        """Универсальный метод выполнения операций"""
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
        """Создает нового пользователя"""

        async def _operation(sess: AsyncSession) -> User:
            user = User(id=user_id, **data)
            sess.add(user)
            await sess.flush()

        return await self.__execute(_operation, True)

    async def update_user(self, user_id: int, data: dict) -> bool:
        """Обновляет данные пользователя, возвращает признак успеха"""

        async def _operation(sess: AsyncSession) -> bool:
            stmt: Update = (
                update(User).where(User.id == user_id).values(**data).execution_options(synchronize_session="fetch")
            )
            result: CursorResult = await sess.execute(stmt)
            return result.rowcount > 0

        return await self.__execute(_operation, True)

    async def user_exists(self, user_id: int) -> bool:
        """Проверяет существование пользователя"""

        async def _operation(sess: AsyncSession) -> bool:
            query: Select = select(exists().where(User.id == user_id))
            result: Result = await sess.execute(query)
            return result.scalar()

        return await self.__execute(_operation)

    async def get_user(self, user_id: int) -> Optional[User]:
        """Возвращает объект User или None"""

        async def _operation(sess: AsyncSession) -> Optional[User]:
            query: Select = select(User).where(User.id == user_id)
            result: Result = await sess.execute(query)
            return result.scalar_one_or_none()

        return await self.__execute(_operation)
