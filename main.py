import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from sqlmodel import Session, select

from connection.connection_service import ConnectionManager
from db.model import create_table, engine, Product, save_product, product_exists
from models.parse_request_model import ParseRequest
from parser.parser import parser_products

# Глобальная переменная для хранения текущего URL
current_url = "https://www.maxidom.ru/catalog/svarochnoe-oborudovanie/"

app = FastAPI()

manager = ConnectionManager()


# WebSocket маршрут
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    """
    Создание таблицы при запуске приложения, если она еще не существует.
    Эта функция вызывается при старте приложения FastAPI.
    """
    create_table()
    asyncio.create_task(run_periodic_parsing())


async def run_periodic_parsing():
    """
    Фоновая задача для периодического парсинга продуктов каждые 12 часов.
    Функция будет выполнять парсинг по глобальному URL и сохранять данные в базу.
    """
    global current_url
    while True:
        await parse_and_save_products(ParseRequest(url=current_url))

        print("Парсинг закончен. Следующий запрос будет через 12 часов.")

        # Пауза на 12 часов перед следующим запуском парсинга
        await asyncio.sleep(12 * 60 * 60)


@app.post("/set_url")
async def set_url(url: str):
    """
    Эндпоинт для изменения URL, который будет использоваться для периодического парсинга.

    Аргументы:
        url (str): Новый URL для парсинга.

    Возвращаемое значение:
        message (str): Сообщение об успешном обновлении URL.
    """
    global current_url
    current_url = url

    return {"message": f"URL для парсинга обновлен на: {current_url}"}


@app.post("/parse")
async def parse_and_save_products(request: ParseRequest):
    """
    Эндпоинт для ручного запуска парсинга товаров с указанного URL.

    Аргументы:
        request (ParseRequest): Запрос с URL для парсинга.

    Возвращаемое значение:
        message (str): Сообщение об успешном завершении парсинга и сохранения данных.
    """
    with Session(engine) as session:
        await parser_products(request.url, session)

    return {"message": "Парсинг завершен и данные сохранены в базу данных."}


@app.get("/products")
async def get_all():
    """
    Эндпоинт для получения списка всех продуктов из базы данных.

    Возвращаемое значение:
        products (List[Product]): Список всех продуктов, хранящихся в базе данных.
    """
    with Session(engine) as session:
        products = session.exec(select(Product)).all()

        await manager.broadcast(f"Все продукты получены")

    return {"products": products}


@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """
    Эндпоинт для получения продукта по id из базы данных.

    Возвращаемое значение:
        product (Product): Продукт, хранящихся в базе данных.
    """
    with Session(engine) as session:
        product = session.get(Product, product_id)
        await manager.broadcast(f"Получен продукт по id {product_id}")

    return {"product": product}


@app.post("/products")
async def add_product(category: str, name: str, price: float):
    """
    Эндпоинт для добавления нового продукта в базу данных.

    Аргументы:
        category (str): Категория продукта.
        name (str): Название продукта.
        price (float): Цена продукта.

    Возвращаемое значение:
        message (str): Сообщение об успешном добавлении продукта.
        product (Product): Добавленный продукт.
    """
    with Session(engine) as session:
        # Проверка на существование продукта
        if product_exists(session, category, name, price):
            raise HTTPException(status_code=400, detail="Product already exists")

        # Создание объекта продукта
        new_product = Product(category=category, name=name, price=price)

        try:
            save_product(session, [new_product])

            # Сообщение об успешном добавлении
            await manager.broadcast(
                f"Добавлен продукт: {new_product.category}, {new_product.name}, ${new_product.price}")

            return {"message": "Продукт успешно добавлен", "product": new_product}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.put("/products/{product_id}")
async def update_product(product_id: int, category: str = None, name: str = None, price: float = None):
    """
    Эндпоинт для редактирования существующего продукта по его идентификатору.

    Аргументы:
        product_id (int): Идентификатор продукта, который нужно редактировать.
        category (str, optional): Новая категория продукта.
        name (str, optional): Новое название продукта.
        price (float, optional): Новая цена продукта.

    Возвращаемое значение:
        message (str): Сообщение об успешном редактировании продукта.
        product (Product): Обновленный продукт.

    Исключения:
        HTTPException: Если продукт с данным ID не найден, будет возвращена ошибка 404.
    """
    with Session(engine) as session:
        product = session.get(Product, product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Обновляем поля, если они переданы в запросе
        if category is not None:
            product.category = category
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price

        session.add(product)
        session.commit()
        session.refresh(product)

        await manager.broadcast(f"Обновлен продукт: {product.category}, {product.name}, {product.price} ₽")

    return {"message": f"Продукт успешно обновлен", "product": product}


@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    """
    Эндпоинт для удаления продукта по его идентификатору.

    Аргументы:
        product_id (int): Идентификатор продукта, который нужно удалить.

    Возвращаемое значение:
        message (str): Сообщение об успешном удалении продукта.

    Исключения:
        HTTPException: Если продукт с данным ID не найден, будет возвращена ошибка 404.
    """
    with Session(engine) as session:
        # Находим продукт по ID
        product = session.get(Product, product_id)

        # Если продукт не найден, выбрасываем ошибку
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Удаляем продукт
        session.delete(product)
        session.commit()

        await manager.broadcast(f"Удален продукт с id {product_id}")

    return {"message": f"Продукт успешно удален"}
