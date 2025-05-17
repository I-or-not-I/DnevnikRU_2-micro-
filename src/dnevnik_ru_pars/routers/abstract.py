"""
Модуль с абстрактным роутером для FastAPI приложений.

"""

from abc import ABC, abstractmethod
from fastapi import APIRouter


class AbstractRouter(ABC):
    """
    Абстрактный базовый класс для создания роутеров FastAPI.

    Наследует:
    - :class:`ABC` из модуля abc
    """

    @abstractmethod
    def __init__(self) -> None:
        """Инициализация абстрактного роутера."""

    @abstractmethod
    def get_router(self) -> APIRouter:
        """Получение сконфигурированного роутера FastAPI.

        :return: Экземпляр APIRouter с зарегистрированными эндпоинтами
        :rtype: :class:`APIRouter`
        """

    @abstractmethod
    def get_endpoints(self) -> tuple:
        """Получение всех эндпоинтов

        :return: список всех эндпоинтов
        :rtype: tuple
        """
