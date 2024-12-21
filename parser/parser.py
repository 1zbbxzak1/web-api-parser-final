import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session

from db.model import product_exists, save_product, Product


async def parser_products(url, session: Session):
    """
    Асинхронный парсер для извлечения данных о продуктах с веб-страницы и сохранения их в базу данных.

    Эта функция извлекает информацию о продуктах (категория, название, цена) с указанного URL и сохраняет их в базе данных.
    Перед добавлением нового продукта в базу данных выполняется проверка на его дублирование.

    Аргументы:
        url (str): URL страницы, с которой будет осуществляться парсинг.
        session (Session): Сессия SQLAlchemy для взаимодействия с базой данных.
    """
    async with httpx.AsyncClient() as client:
        while url:
            # Отправляем GET-запрос на указанную страницу
            response = await client.get(url)

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break

            # Создаем объект BeautifulSoup для парсинга HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем категорию товара
            category_tag = soup.find("span", itemprop="name")
            category = category_tag.get_text(strip=True) if category_tag else "No category"

            # Извлекаем все товары на текущей странице
            items = soup.find_all('article', class_='l-product')
            parsed_products = []

            for item in items:
                # Извлекаем название товара
                name_tag = item.find('span', itemprop='name')
                name = name_tag.get_text(strip=True) if name_tag else "No name"

                # Извлекаем цену товара
                price_tag = item.find('span', itemprop='price')
                price = price_tag.get_text(strip=True) if price_tag else "No price"

                # Проверка на дублирование в БД перед добавлением
                if not product_exists(session, category, name, price):
                    # Сохраняем новый продукт
                    product = Product(category=category, name=name, price=price)
                    parsed_products.append(product)
                else:
                    print(f"Skipping duplicate product: {name} - {price}")

            if parsed_products:
                save_product(session, parsed_products)

            # Переход к следующей странице, если она существует
            next_page = soup.select_one('#navigation_2_next_page[href]')
            if next_page:
                url = "https://www.maxidom.ru" + next_page['href']
            else:
                url = None  # Завершить цикл, если следующей страницы нет
