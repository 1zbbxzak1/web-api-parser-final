from pydantic import BaseModel


class ParseRequest(BaseModel):
    """
    Модель данных для запроса на парсинг, содержащая URL для парсинга.

    Атрибуты:
        url (str): URL страницы для парсинга.
    """
    url: str
