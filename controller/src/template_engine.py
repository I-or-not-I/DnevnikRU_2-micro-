"""
Модуль для работы с шаблонами на основе Jinja2.
"""

import abc
import logging
from typing import Optional
from jinja2 import Environment, Template, FileSystemLoader


class AbstractTemplateEngine(abc.ABC):
    """Абстрактный базовый класс для движка шаблонов.

    .. method:: render(template_path, data)
        :abstractmethod:
    """

    @abc.abstractmethod
    def __init__(self, templates_folder_path: str) -> None:
        """Инициализация движка шаблонов.

        :param templates_folder_path: Путь к директории с шаблонами
        :type templates_folder_path: str
        """

    @abc.abstractmethod
    def render(self, template_path: str, data: dict = None) -> str:
        """Рендеринг шаблона с данными.

        :param template_path: Относительный путь к файлу шаблона
        :param data: Данные для подстановки в шаблон
        :type template_path: str
        :type data: Optional[dict]
        :return: Обработанный шаблон в виде строки
        :rtype: str

        .. note::
            Файл шаблона должен находиться в указанной при инициализации директории
        """


class TemplateEngine(AbstractTemplateEngine):
    """Конкретная реализация движка шаблонов с использованием Jinja2.

    :param templates_folder_path: Путь к папке с шаблонами
    :type templates_folder_path: str
    """

    def __init__(self, templates_folder_path: str) -> None:
        logging.debug("Инициализация TemplateEngine")
        self.__environment = Environment(loader=FileSystemLoader(templates_folder_path))

    def render(self, template_path: str, data: Optional[dict] = None) -> str:
        """Рендеринг шаблона с данными.

        :param data: По умолчанию используется пустой словарь
        :raises TemplateNotFound: Если файл шаблона не существует
        """
        super().render(template_path)
        template: Template = self.__environment.get_template(template_path)
        return template.render(data=data)
