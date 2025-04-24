import abc
import requests
from json import dumps


class AbstractApi(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def verify_data_get_personal_data(self, data: dict["login":str, "password":str]) -> dict | bool:
        pass

    @abc.abstractmethod
    def get_marks(self, data: dict) -> dict | bool:
        pass


class Api(AbstractApi):
    def __init__(self, parser_ip: str) -> None:
        self.__parser_ip: str = parser_ip

    def __get_data(self, path: str, data: dict) -> dict | bool:
        try:
            response: requests.Response = requests.post(f"{self.__parser_ip}/{path}", data=self.__dict_to_json(data))
            response.raise_for_status()
        except requests.exceptions.HTTPError :
            return False

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return False

    def verify_data_get_personal_data(self, data: dict) -> dict | bool:
        path: str = "verify_data_get_personal_data"
        return self.__get_data(path, data)

    def get_marks(self, data: dict) -> dict | bool:
        path: str = "get_marks"
        return self.__get_data(path, data)

    @staticmethod
    def __dict_to_json(data: dict) -> str:
        return dumps(data, ensure_ascii=False)
