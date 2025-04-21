from pydantic import BaseModel, BaseModel


class UserData(BaseModel):
    id: int | None = None
    password: str
    login: str
    person_id: int | None = None
    school_id: int | None = None
    group_id: int | None = None
    cookies: dict | None = None
