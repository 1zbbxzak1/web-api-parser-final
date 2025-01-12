# web-api-parser-final

Это FastAPI-приложение для парсинга товаров с веб-страницы и сохранения их в базе данных. Приложение использует SQLModel
для работы с базой данных и httpx + BeautifulSoup для парсинга HTML. Оно поддерживает автоматический парсинг товаров с
заданного URL каждые 12 часов, а также предоставляет API для ручного запуска парсинга и управления товарами в базе
данных.

## Функции приложения:

- Автоматический парсинг товаров с веб-страницы через заданный URL каждые 12 часов.
- Ручной запуск парсинга товаров через API.
- Возможность изменения URL для автоматического парсинга через API.
- Управление товарами в базе данных (добавление, удаление, обновление, получение списка товаров, получение одного
  товара).

## API

### 1. Изменение URL для парсинга

- **Метод**: `POST`
- **Эндпоинт**: `/set_url`
- **Тело запроса**:
    ```json
    {
      "url": "https://www.example.com/products"
    }
    ```
- **Ответ**:
    ```json
    {
      "message": "URL for parsing updated to: https://www.example.com/products"
    }
    ```

### 2. Ручной запуск парсинга

- **Метод**: `POST`
- **Эндпоинт**: `/parse`
- **Тело запроса**:
    ```json
    {
      "url": "https://www.example.com/products"
    }
    ```
- **Ответ**:
    ```json
    {
      "message": "Products parsed and saved successfully"
    }
    ```

### 3. Получение списка всех товаров

- **Метод**: `GET`
- **Эндпоинт**: `/products`
- **Ответ**:
    ```json
    {
      "products": [
        {
          "id": 1,
          "category": "Electronics",
          "name": "Smartphone",
          "price": 599.99
        },
        ...
      ]
    }
    ```

### 4. Получение одного товара

- **Метод**: `GET`
- **Эндпоинт**: `/products/{product_id}`
- **Параметры запроса**:
    - `id`: id продукта _(int)_
- **Ответ**:
    ```json
    {
      "products": [
        {
          "id": 1,
          "category": "Electronics",
          "name": "Smartphone",
          "price": 599.99
        },
        ...
      ]
    }
    ```

### 4. Добавление нового товара

- **Метод**: `POST`
- **Эндпоинт**: `/products`
- **Параметры запроса**:
    - `category`: категория продукта _(string)_
    - `name`: название продукта _(string)_
    - `price`: цена продукта _(number)_
- **Ответ**:
    ```json
    {
      "message": "Product added successfully",
      "product": {
        "id": 1,
        "category": "Electronics",
        "name": "Smartphone",
        "price": 599.99
      }
    }
    ```

### 5. Удаление товара

- **Метод**: `DELETE`
- **Эндпоинт**: `/products/{product_id}`
- **Параметры запроса**:
    - `product_id`: ID продукта для удаления _(integer)_
- **Ответ**:
    ```json
    {
      "message": "Product with id 1 deleted successfully"
    }
    ```

### 6. Обновление товара

- **Метод**: `PUT`
- **Эндпоинт**: `/products/{product_id}`
- **Параметры запроса**:
    - `product_id`: ID продукта для обновления _(integer)_
    - `category`: новая категория продукта _(string, optional)_
    - `name`: новое название продукта _(string, optional)_
    - `price`: новая цена продукта _(number, optional)_
- **Ответ**:
    ```json
    {
      "message": "Product with id 1 updated successfully",
      "product": {
        "id": 1,
        "category": "Electronics",
        "name": "Updated Smartphone",
        "price": 649.99
      }
    }
    ```

## Проверка WebSocket

### Запуск в консоли разработчика

```javascript
const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
    console.log("WebSocket connection opened");
};

socket.onmessage = (event) => {
    console.log("Message from server:", event.data);
};

socket.onclose = () => {
    console.log("WebSocket connection closed");
};
```

### Запуск с помощью wscat

1. Установить wscat с помощью npm:

```bash
npm install -g wscat
```

2. Подключиться к WebSocket серверу:

```bash
wscat -c ws://127.0.0.1:8000/ws
```

## Периодический парсинг

Приложение выполняет парсинг товаров с веб-страницы каждые 12 часов. Для этого используется фоновая задача, которая
автоматически выполняет парсинг с текущего URL. Вы можете изменить URL для парсинга через эндпоинт `/set_url`.

## Технологии

- **FastAPI** — веб-фреймворк для создания API.
- **SQLModel** — ORM для работы с базой данных.
- **httpx** — асинхронные HTTP-запросы.
- **BeautifulSoup** — библиотека для парсинга HTML.
- **SQLite** — база данных для хранения продуктов.
