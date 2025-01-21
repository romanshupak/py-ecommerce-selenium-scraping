from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import requests


BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: str


def parse_single_product(product: Tag):
    """Parse a single product and returns Product object"""
    title_element = product.select_one("a.title")
    title = title_element["title"] if title_element else "No title"

    description_element = product.select_one("p.description")
    description = description_element.text if description_element else "No description"

    price_element = product.select_one("h4.price")
    price = float(price_element.text.replace("$", "") if price_element else "No price")

    rating_element = product.select_one("p[data-rating]")
    rating = int(rating_element["data-rating"]) if rating_element else "No rating"

    num_of_reviews_element = product.select_one("p.review-count")
    num_of_reviews = num_of_reviews_element.text if num_of_reviews_element else "No number of reviews"

    return Product(title=title, description=description, price=price, rating=rating, num_of_reviews=num_of_reviews)


def get_all_products() -> list[Product]:
    response = requests.get(HOME_URL)
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
