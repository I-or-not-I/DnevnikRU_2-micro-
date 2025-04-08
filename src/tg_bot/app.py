import logging
from utils.logger import Logger

from src.bot import AbstractTgBot, TgBot
from src.api import AbstractApi, Api

from config import TOKEN, CONTROLLER_IP


def main() -> None:
    Logger(logging.DEBUG)

    api: AbstractApi = Api(CONTROLLER_IP)
    bot: AbstractTgBot = TgBot(TOKEN, api)

    bot.run()


if __name__ == "__main__":
    main()
