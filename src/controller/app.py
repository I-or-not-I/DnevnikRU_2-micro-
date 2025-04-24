import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils.logger import Logger
from src.controller import AbstractController, Controller
from src.db import AbstractDb, Db
from src.template_engine import AbstractTemplateEngine, TemplateEngine
from src.api import AbstractApi, Api
from src.markups import AbstractMarkups, Markups
from routers import abstract, base, bot

from config import DB_DATA, PARSER_IP


def main() -> None:
    Logger(logging.DEBUG)

    app: FastAPI = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Изменить
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    db: AbstractDb = Db(DB_DATA)
    db.create_data_table()
    template_engine: AbstractTemplateEngine = TemplateEngine("templates")
    api: AbstractApi = Api(PARSER_IP)
    markups: AbstractMarkups = Markups()
    controller: AbstractController = Controller(api, db, template_engine, markups)

    routers: tuple[abstract.AbstractRouter] = (base.Router(), bot.Router(controller))
    for router in routers:
        app.include_router(router.get_router())

    uvicorn.run(app, host="0.0.0.0", port=8019)  # Изменить


if __name__ == "__main__":
    main()
