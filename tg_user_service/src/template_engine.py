"""
Модуль для работы с шаблонами на основе Jinja2.

Предоставляет:
- Абстрактный интерфейс для движка шаблонов
- Конкретную реализацию с использованием Jinja2
- Рендеринг шаблонов с подстановкой данных

Основные функции:
- Инициализация среды шаблонов
- Загрузка шаблонов из файловой системы
- Рендеринг шаблонов с передачей данных

Компоненты:
    AbstractTemplateEngine: Абстрактный интерфейс движка шаблонов
    TemplateEngine: Конкретная реализация на базе Jinja2

Зависимости:
    Jinja2: Библиотека для работы с шаблонами
    logging: Для логирования процесса инициализации
"""

import abc
import logging
from typing import Optional
from jinja2 import Environment, Template, FileSystemLoader, TemplateNotFound


class AbstractTemplateEngine(abc.ABC):
    """
    Абстрактный базовый класс для движка шаблонов.

    :param templates_folder_path: Путь к директории с шаблонами
    :type templates_folder_path: str
    """

    @abc.abstractmethod
    def __init__(self, templates_folder_path: str) -> None:
        """
        Абстрактный конструктор движка шаблонов.

        :param templates_folder_path: Путь к папке с шаблонами
        :type templates_folder_path: str
        :meta abstract:
        """

    @abc.abstractmethod
    def render(self, template_path: str, data: dict | None = None) -> str:
        """
        Абстрактный метод рендеринга шаблона.

        :param template_path: Относительный путь к файлу шаблона
        :param data: Данные для подстановки в шаблон
        :type template_path: str
        :type data: Optional[dict]
        :return: Обработанный шаблон в виде строки
        :rtype: str
        :meta abstract:

        .. note::
            Файл шаблона должен находиться в указанной при инициализации директории.
            Если данные не переданы, используется пустой словарь.
        """


class TemplateEngine(AbstractTemplateEngine):
    """
    Конкретная реализация движка шаблонов с использованием Jinja2.

    :param templates_folder_path: Путь к папке с шаблонами
    :type templates_folder_path: str
    :returns: Инициализированный экземпляр движка шаблонов
    :rtype: TemplateEngine
    """

    def __init__(self, templates_folder_path: str) -> None:
        """
        Инициализация движка шаблонов.

        :param templates_folder_path: Путь к директории с шаблонами
        :type templates_folder_path: str
        """
        logging.debug("Инициализация TemplateEngine")
        self.__environment = Environment(loader=FileSystemLoader(templates_folder_path))

    def render(self, template_path: str, data: Optional[dict] = None) -> str:
        """
        Рендеринг шаблона с данными.

        :param template_path: Относительный путь к файлу шаблона
        :param data: Данные для подстановки в шаблон (по умолчанию {})
        :type template_path: str
        :type data: Optional[dict]
        :return: Обработанный шаблон в виде строки
        :rtype: str
        :raises TemplateNotFound: Если файл шаблона не существует

        Пример использования:
            engine = TemplateEngine("templates")
            result = engine.render("welcome.j2", {"name": "John"})
        """
        super().render(template_path)
        template: Template = self.__environment.get_template(template_path)
        return template.render(data=data)
