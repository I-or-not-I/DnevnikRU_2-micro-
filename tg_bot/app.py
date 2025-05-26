"""
Основной модуль запуска телеграм-бота.
"""

from os import environ
from utils.logger import Logger
from src.bot import AbstractTgBot, TgBot
from src.api import AbstractApi, Api
from config import CONTROLLER_IP, LOGGING_LEVEL


def main() -> None:
    """Основная функция инициализации и запуска бота.

    Выполняет:
    1. Настройку системы логирования
    2. Инициализацию API
    3. Создание экземпляра бота
    4. Запуск основного цикла бота

    :raises ConnectionError: При проблемах с подключением к Telegram API
    :raises ValueError: При невалидных параметрах конфигурации
    """
    Logger(LOGGING_LEVEL)

    api: AbstractApi = Api(CONTROLLER_IP)

    TOKEN = environ.get("TOKEN")
    bot: AbstractTgBot = TgBot(TOKEN, api)

    bot.run()


if __name__ == "__main__":
    main()
