from typing import List
from pydantic import BaseModel, Field


class From(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: str
    username: str
    language_code: str


class Chat(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    type: str


class Entity(BaseModel):
    offset: int
    length: int
    type: str


class Message(BaseModel):
    message_id: int
    from_: From = Field(..., alias="from")
    chat: Chat
    date: int
    text: str
    entities: List[Entity] = None
    login: str = None
    password: str = None
