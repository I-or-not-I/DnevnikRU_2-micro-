from jinja2 import Environment, Template, FileSystemLoader
import abc
import logging


class AbstractTemplateEngine(abc.ABC):
    @abc.abstractmethod
    def __init__(self, templates_folder_path) -> None:
        logging.debug("Инициализация TemplateEngine")

    @abc.abstractmethod
    def render(self, template_path: str, data: dict = None) -> str:
        logging.debug(f"Конвертация шаблона {template_path}")


class TemplateEngine(AbstractTemplateEngine):
    def __init__(self, templates_folder_path: str) -> None:
        super().__init__(templates_folder_path)
        self.__environment = Environment(loader=FileSystemLoader(templates_folder_path))

    def render(self, template_path: str, data: dict = {}) -> str:
        super().render(template_path)
        template: Template = self.__environment.get_template(template_path)
        return template.render(data=data)
