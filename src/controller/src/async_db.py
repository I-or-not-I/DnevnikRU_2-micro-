"""
Асинхронный модуль для работы с PostgreSQL.
"""

import abc
from typing import Any, Callable, Dict, Optional
import asyncpg


class AbstractDb(abc.ABC):
    """Абстрактный базовый класс для асинхронной работы с базой данных."""

    @abc.abstractmethod
    async def create_data_table(self, connection: Optional[asyncpg.Connection] = None) -> None:
        """Создает таблицу данных если она не существует."""

    @abc.abstractmethod
    async def create_new_user(self, user_id: int, data: Dict, connection: Optional[asyncpg.Connection] = None) -> None:
        """Добавляет нового пользователя в БД."""

    @abc.abstractmethod
    async def update_user_data(self, user_id: int, data: Dict, connection: Optional[asyncpg.Connection] = None) -> None:
        """Обновляет данные существующего пользователя."""

    @abc.abstractmethod
    async def user_in_table(self, user_id: int, connection: Optional[asyncpg.Connection] = None) -> bool:
        """Проверяет наличие пользователя в БД."""

    @abc.abstractmethod
    async def get_user_data(self, user_id: int, connection: Optional[asyncpg.Connection] = None) -> Dict:
        """Возвращает данные пользователя в виде словаря."""


class Db(AbstractDb):
    """Асинхронная реализация работы с PostgreSQL."""

    def __init__(self, db_config: Dict) -> None:
        self._db_config = db_config
        self._columns = {
            "id": "INTEGER PRIMARY KEY",
            "password": "TEXT",
            "login": "TEXT",
            "person_id": "TEXT",
            "school_id": "TEXT",
            "group_id": "TEXT",
            "cookies": "JSONB",
        }

    async def _manage_connection(self, func: Callable, **kwargs) -> Any:
        """Управляет подключением и транзакциями."""
        conn = await asyncpg.connect(**self._db_config)
        try:
            async with conn.transaction():
                return await func(connection=conn, **kwargs)
        finally:
            await conn.close()

    async def create_data_table(self, connection: Optional[asyncpg.Connection] = None) -> None:
        if not connection:
            return await self._manage_connection(self.create_data_table)

        columns = ", ".join(f"{k} {v}" for k, v in self._columns.items())
        await connection.execute(f"CREATE TABLE IF NOT EXISTS data ({columns})")

    async def create_new_user(self, user_id: int, data: Dict, connection: Optional[asyncpg.Connection] = None) -> None:
        if not connection:
            return await self._manage_connection(self.create_new_user, user_id=user_id, data=data)

        data["id"] = user_id
        columns = ", ".join(data.keys())
        values = ", ".join(f"${i+1}" for i in range(len(data)))
        await connection.execute(f"INSERT INTO data ({columns}) VALUES ({values})", *data.values())

    async def update_user_data(self, user_id: int, data: Dict, connection: Optional[asyncpg.Connection] = None) -> None:
        if not connection:
            return await self._manage_connection(self.update_user_data, user_id=user_id, data=data)

        updates = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(data))
        await connection.execute(f"UPDATE data SET {updates} WHERE id = ${len(data)+1}", *data.values(), user_id)

    async def user_in_table(self, user_id: int, connection: Optional[asyncpg.Connection] = None) -> bool:
        if not connection:
            return await self._manage_connection(self.user_in_table, user_id=user_id)

        return await connection.fetchval("SELECT EXISTS(SELECT 1 FROM data WHERE id = $1)", user_id)

    async def get_user_data(self, user_id: int, connection: Optional[asyncpg.Connection] = None) -> Dict:
        if not connection:
            return await self._manage_connection(self.get_user_data, user_id=user_id)

        row = await connection.fetchrow(f"SELECT {', '.join(self._columns)} FROM data WHERE id = $1", user_id)
        return dict(row) if row else {}
