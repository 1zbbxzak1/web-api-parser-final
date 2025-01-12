from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, create_engine, Session, select


# Определение модели данных для SQLModel
class Product(SQLModel, table=True):
    """
    Модель данных для продукта, которая соответствует таблице в базе данных.

    Атрибуты:
        id (Optional[int]): Идентификатор продукта (автоматически генерируемый ключ).
        category (str): Категория продукта.
        name (str): Название продукта.
        price (float): Цена продукта.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    name: str
    price: float


DATABASE_URL = "sqlite:///./products.db"

# Создание объекта подключения к базе данных
engine = create_engine(DATABASE_URL, echo=False)


def create_table():
    """
    Создает таблицу в базе данных, если она еще не существует.

    Эта функция инициализирует таблицу `Product`, используя метаданные,
    которые были определены в классе `Product`.
    """
    SQLModel.metadata.create_all(bind=engine)


# Простой запрос для проверки существования продукта по имени и цене
def product_exists(session: Session, category: str, name: str, price: float) -> bool:
    """
    Проверяет, существует ли продукт с заданным именем и ценой в базе данных.

    Аргументы:
        session (Session): Сессия SQLAlchemy, через которую осуществляется взаимодействие с базой данных.
        category (str): Категория продукта.
        name (str): Название продукта.
        price (float): Цена продукта.

    Возвращаемое значение:
        bool: Возвращает `True`, если продукт с таким именем и ценой существует в базе данных, иначе `False`.
    """
    statement = select(Product).where(Product.category == category, Product.name == name, Product.price == price)
    result = session.exec(statement).first()
    return result is not None


def save_product(session: Session, products: list[Product]):
    """
    Сохраняет список продуктов в базу данных одной транзакцией.

    Аргументы:
        session (Session): Сессия SQLAlchemy для взаимодействия с базой данных.
        products (list[Product]): Список объектов Product для добавления.
    """
    try:
        session.add_all(products)
        session.commit()
    except IntegrityError:
        session.rollback()
        print("Duplicate entries detected, skipping...")
