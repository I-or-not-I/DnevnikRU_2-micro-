import abc
from typing import Any, Callable
from psycopg2 import connect
from psycopg2.extensions import cursor


class AbstractDb(abc.ABC):
    @abc.abstractmethod
    def __init__(self, data_path: str) -> None:
        pass

    @abc.abstractmethod
    def create_data_table(self, cursor: cursor = None) -> None:
        pass

    @abc.abstractmethod
    def create_new_user(self, id: int, data: dict, cursor: cursor = None) -> None:
        pass

    @abc.abstractmethod
    def update_user_data(self, id: int, data: dict, cursor: cursor = None) -> None:
        pass

    @abc.abstractmethod
    def user_in_table(self, id: int, cursor: cursor = None) -> bool:
        pass

    @abc.abstractmethod
    def get_user_data(self, id: int, cursor: cursor = None) -> dict:
        pass


class Db(AbstractDb):
    def __init__(self, db_data: dict) -> None:
        self.__db_data: dict = db_data
        self.__columns: dict = {
            "id": "INTEGER",
            "password": "TEXT",
            "login": "TEXT",
            "person_id": "TEXT",
            "school_id": "TEXT",
            "group_id": "TEXT",
            "cookies": "JSON",
        }

    def __connection(self, func: Callable, id: int = None, data: dict = None, commit: bool = False) -> Any:
        with connect(**self.__db_data) as connection:
            with connection.cursor() as cursor:
                ans: Any = func(cursor=cursor, **{k: v for k, v in {"id": id, "data": data}.items() if v is not None})
                if commit:
                    connection.commit()
                return ans

    def create_data_table(self, cursor: cursor = None) -> None:
        if not cursor:
            return self.__connection(self.create_data_table, commit=True)
        enquiry: str = f"CREATE TABLE IF NOT EXISTS data ({', '.join(f'{k} {v}' for k, v in self.__columns.items())})"
        cursor.execute(enquiry)

    def create_new_user(self, id: int, data: dict, cursor: cursor = None) -> None:
        data["id"] = id
        if not cursor:
            return self.__connection(func=self.create_new_user, id=id, data=data, commit=True)
        enquiry: str = "INSERT INTO data (%s) VALUES (%s)" % (", ".join(data.keys()), ", ".join(["%s"] * len(data)))
        cursor.execute(enquiry, list(data.values()))

    def update_user_data(self, id: int, data: dict, cursor: cursor = None) -> None:
        if not cursor:
            return self.__connection(func=self.update_user_data, id=id, data=data, commit=True)
        cursor.execute(f"UPDATE data SET {', '.join(f"{k} = '{v}'" for k, v in data.items())} WHERE id = {id}")

    def user_in_table(self, id: int, cursor: cursor = None) -> bool:
        if not cursor:
            return self.__connection(func=self.user_in_table, id=id)
        cursor.execute(f"SELECT id FROM data WHERE id = '{id}'")
        data: int = cursor.fetchone()
        return data is not None

    def get_user_data(self, id: int, cursor: cursor = None) -> dict:
        if not cursor:
            return self.__connection(func=self.get_user_data, id=id)
        cursor.execute(f"SELECT {', '.join(self.__columns.keys())} FROM data WHERE id = {id}")
        data: dict = dict(zip(self.__columns.keys(), cursor.fetchone()))
        return data
