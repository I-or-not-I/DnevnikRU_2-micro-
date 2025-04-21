import abc
import re
from json import dumps, loads
import requests
from bs4 import BeautifulSoup

from models.user_data import UserData


class AbstractParser(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def get_marks(data: UserData) -> dict | bool:
        pass

    @abc.abstractmethod
    def get_cookies_person_school_group_id(self, data: UserData) -> dict | bool:
        pass


class Parser(AbstractParser):
    @staticmethod
    def get_marks(user_data: UserData) -> dict | bool:
        url: str = f"https://dnevnik.ru/api/v2/marks/school/{user_data.school_id}/person/{user_data.person_id}"
        try:
            subjects: list = requests.get(url, cookies=user_data.cookies).json()
        except requests.exceptions.JSONDecodeError:
            return False
        marks: dict = {}
        for subject in subjects["subjects"]:
            marks[subject["name"]] = []
            local_marks: list = []
            for work in subject["works"]:
                [local_marks.append(mark["value"]) for mark in work["marks"]]
            marks[subject["name"]].append(local_marks)
            if local_marks:
                marks[subject["name"]].append(subject["average"]["value"])

        return marks

    def get_cookies_person_school_group_id(self, user_data: UserData) -> dict | bool:
        session: requests.Session = self.__get_registered_session(user_data.login, user_data.password)

        url = "https://dnevnik.ru/userfeed"
        html: str = session.get(url).text
        soup = BeautifulSoup(html, features="lxml")

        body: BeautifulSoup | None = soup.find("body", {"class": "page-body"})
        if body is None:
            return False

        script: str = body.find_all("script")[11]
        data: str = re.search("window.__USER__START__PAGE__INITIAL__STATE__ = {(.*)}", script.text)
        initial_state: dict = loads("{" + data[1] + "}")
        persons_context: dict = initial_state["analytics"]

        ans_data: dict = {}
        ans_data["person_id"] = persons_context["personId"]
        ans_data["school_id"] = persons_context["schoolId"]
        ans_data["group_id"] = persons_context["groupId"]
        ans_data["cookies"] = dumps(session.cookies.get_dict())

        return ans_data

    @staticmethod
    def __get_registered_session(login: str, password: str) -> requests.Session:
        session = requests.Session()

        data: dict = {
            "exceededAttempts": False,
            "ReturnUrl": None,
            "FingerprintId": None,
            "login": f"{login}",
            "password": f"{password}",
            "Captcha.Input": None,
            "Captcha.Id": None,
        }
        url = "https://login.dnevnik.ru/login/esia/rostov"
        session.post(url, data)

        return session
