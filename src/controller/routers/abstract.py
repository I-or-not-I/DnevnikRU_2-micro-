"""
Модуль с абстрактным роутером для FastAPI приложений.
"""

from fastapi import APIRouter
from abc import ABC, abstractmethod


class AbstractRouter(ABC):
    """Абстрактный базовый класс для создания роутеров FastAPI.

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
