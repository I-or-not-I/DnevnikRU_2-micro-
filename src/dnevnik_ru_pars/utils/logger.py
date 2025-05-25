import logging
from typing import Self


class Logger:
    _instance = None

    def __new__(cls, level: int) -> Self:
        if not isinstance(cls._instance, cls):
            cls._instance: Self = super().__new__(cls)
        return cls._instance

    def __init__(self, level: int) -> None:
        self.__logging_basic_config(level)

    @staticmethod
    def __logging_basic_config(level: int) -> None:
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("app.log", encoding="utf-8"), logging.StreamHandler()],
        )
