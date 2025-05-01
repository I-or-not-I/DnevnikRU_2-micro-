"""
Основной модуль запуска телеграм-бота.
"""

import logging
from utils.logger import Logger
from src.bot import AbstractTgBot, TgBot
from src.api import AbstractApi, Api
from config import TOKEN, CONTROLLER_IP


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
    Logger(logging.DEBUG)

    api: AbstractApi = Api(CONTROLLER_IP)
    bot: AbstractTgBot = TgBot(TOKEN, api)

    bot.run()


if __name__ == "__main__":
    main()
