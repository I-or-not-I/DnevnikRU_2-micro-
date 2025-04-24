from fastapi import APIRouter

from routers.abstract import AbstractRouter


class Router(AbstractRouter):
    def __init__(self) -> None:
        self.__router: APIRouter = APIRouter()
        self.__routs_register()

    def __routs_register(self) -> None:
        self.__router.add_api_route("/", self.__ping, methods=["GET"])

    async def __ping(self) -> str:
        return "PONG"

    def get_router(self) -> APIRouter:
        return self.__router
