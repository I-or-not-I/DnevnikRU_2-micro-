from fastapi import APIRouter
from abc import ABC, abstractmethod


class AbstractRouter(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_router(self) -> APIRouter:
        pass
