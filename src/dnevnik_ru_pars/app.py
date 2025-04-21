import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from utils.logger import Logger
from routers import abstract, base, dnevnik
from src.parser import AbstractParser, Parser


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

    parser: AbstractParser = Parser()

    routers: tuple[abstract.AbstractRouter] = (base.Router(), dnevnik.Router(parser))
    for router in routers:
        app.include_router(router.get_router())

    uvicorn.run(app, host="0.0.0.0", port=8022)  # Изменить


if __name__ == "__main__":
    main()
