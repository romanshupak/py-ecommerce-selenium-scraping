from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")
COMPUTER_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers")
LAPTOP_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers/laptops")
TABLET_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/computers/tablets")

_driver: WebDriver | None = None


def get_driver() -> WebDriver:
    return _driver


def set_driver(new_driver: WebDriver) -> None:
    global _driver
    _driver = new_driver


@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int
    additional_info: dict


def parse_hdd_block_prices(product_sup: Tag) -> dict[str, float]:
    absolute_url = urljoin(BASE_URL, product_sup.select_one("a.title")["href"])
    driver = get_driver()
    driver.get(absolute_url)
    swatches = driver.find_element(By.CLASS_NAME, "swatches")
    buttons = swatches.find_elements(By.TAG_NAME, "button")
    prices = {}
    for button in buttons:
        if not button.get_property("disabled"):
            button.click()
            prices[button.get_property("value")] = float(
                driver.find_element(
                    By.CLASS_NAME, "price"
                ).text.replace("$", "")
            )
    return prices


    # driver find swatches
    # iterate through buttons -> click button if clickable -> get price

    # pass


def parse_single_product(product: Tag, use_data_rating: bool = False) -> Product:
    """Parse a single product and returns Product object"""
    title_element = product.select_one("a.title")
    title = title_element["title"] if title_element else "No title"

    description_element = product.select_one("p.description")
    description = description_element.text if description_element else "No description"

    price_element = product.select_one("h4.price")
    price = float(price_element.text.replace("$", "") if price_element else "No price")

    if use_data_rating:
        # use selector for HOME_URL
        rating_element = product.select_one("p[data-rating]")
        rating = int(rating_element["data-rating"]) if rating_element else "No rating"
    else:
        # use selector for LAPTOP_URL
        rating_stars = product.select("div.ratings p span.ws-icon-star")
        rating = len(rating_stars)

    num_of_reviews_element = product.select_one("p.review-count")
    num_of_reviews = int(num_of_reviews_element.text.split()[0]) if num_of_reviews_element else "No number of reviews"

    hdd_prices = parse_hdd_block_prices(product)

    return Product(
        title=title,
        description=description,
        price=price,
        rating=rating,
        num_of_reviews=num_of_reviews,
        additional_info={"hdd_prices": hdd_prices}
    )


# def get_all_products() -> list[Product]:
#     """Scrape all products from the HOME_URL"""
#     response = requests.get(HOME_URL)
#     response.raise_for_status()
#     soup = BeautifulSoup(response.content, "html.parser")
#
#     # Get all products on the home page
#     product_elements = soup.select("div.thumbnail")
#     # Використовуємо `use_data_rating=True` для парсингу рейтингу з атрибута `data-rating`
#     products = [parse_single_product(product, use_data_rating=True) for product in product_elements]
#     return products

def get_all_products(url: str, use_data_rating: bool = False, is_dynamic: bool = False) -> list[Product]:
    """
    Scrape all products from the given URL.

    Args:
        url (str): The URL of the page to scrape.
        use_data_rating (bool): Whether to parse rating from `data-rating`.
        is_dynamic (bool): Whether the page is dynamically loaded (requires Selenium).

    Returns:
        list[Product]: List of parsed products.
    """
    if is_dynamic:
        # Використовуємо Selenium для динамічних сторінок
        driver = get_driver()
        driver.get(url)

        while True:
            try:
                more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
                )
                ActionChains(driver).move_to_element(more_button).click(more_button).perform()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "btn-primary"))
                )
            except Exception:
                print("No more products to load or button not found.")
                break

        soup = BeautifulSoup(driver.page_source, "html.parser")
    else:
        # Використовуємо requests для статичних сторінок
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

    # Парсимо продукти
    product_elements = soup.select("div.thumbnail")
    products = [parse_single_product(product, use_data_rating=use_data_rating) for product in product_elements]
    return products


# parsing laptops with Selenium
# def get_all_laptops():
#     driver = webdriver.Chrome()
#     driver.get(LAPTOP_URL)
#
#     while True:
#         try:
#             more_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.CLASS_NAME, "btn-primary"))
#             )
#             ActionChains(driver).move_to_element(more_button).click(more_button).perform()
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "btn-primary"))
#             )
#         except Exception:
#             print("No more products to load or button not found.")
#             break  # Якщо кнопка більше недоступна, виходимо з циклу
#
#     # Отримуємо весь HTML сторінки
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     driver.quit()
#
#     # Знаходимо всі продукти
#     product_elements = soup.select("div.thumbnail")
#     # Використовуємо `use_data_rating=False` для парсингу рейтингу через зірки
#     products = [parse_single_product(product, use_data_rating=False) for product in product_elements]
#     return products


# def main():
#     with webdriver.Chrome() as driver:
#         set_driver(driver)
#
#         print("Scraping all products from HOME_URL...")
#         home_products = get_all_products()
#         print(f"Found {len(home_products)} products on the home page.")
#
#         print("Scraping all laptops from LAPTOP_URL...")
#         laptop_products = get_all_laptops()
#         print(f"Found {len(laptop_products)} laptops on the laptops page.")
#
#         all_products = home_products + laptop_products
#         for product in all_products:
#             print(product)

def main():
    with webdriver.Chrome() as driver:
        set_driver(driver)

        # Scraping products from different pages
        print("Scraping all products from HOME_URL...")
        home_products = get_all_products(HOME_URL, use_data_rating=True)

        print("Scraping all computers from COMPUTER_URL...")
        computer_products = get_all_products(COMPUTER_URL, use_data_rating=False)

        print("Scraping all laptops from LAPTOP_URL...")
        laptop_products = get_all_products(LAPTOP_URL, use_data_rating=False, is_dynamic=True)

        print("Scraping all laptops from TABLET_URL...")
        tablet_products = get_all_products(TABLET_URL, use_data_rating=False, is_dynamic=True)

        all_products = home_products + computer_products + laptop_products + tablet_products
        print(f"Total products scraped: {len(all_products)}")

        for product in all_products:
            print(product)


if __name__ == "__main__":
    # get_all_products()
    main()
