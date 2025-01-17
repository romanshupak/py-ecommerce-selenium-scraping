from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import requests


BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")


@dataclass
class Product:
    title: str
    # description: str
    # price: float
    # rating: int
    # num_of_reviews: int


def parse_single_product(product: Tag):
    """Parse a single product and returns Product object"""
    title_element = product.select_one("a.title")
    title = title_element.text.strip() if title_element else "No title"
    print(f"Title: {title}")

    return Product(title=title)


def get_all_products() -> list[Product]:
    response = requests.get(HOME_URL)
    print(HOME_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Отримуємо всі продукти на сторінці
    product_elements = soup.select("div.thumbnail")
    products = [parse_single_product(product) for product in product_elements]
    return products


def main():
    products = get_all_products()
    for product in products:
        print(product)


if __name__ == "__main__":
    # get_all_products()
    main()
