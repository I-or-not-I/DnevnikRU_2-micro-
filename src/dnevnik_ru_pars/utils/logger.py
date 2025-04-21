import logging


class Logger:
    def __init__(self, level: int) -> None:
        self.__logging_basic_config(level)

    @staticmethod
    def __logging_basic_config(level: int) -> None:
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("app.log", encoding="utf-8"), logging.StreamHandler()],
        )
