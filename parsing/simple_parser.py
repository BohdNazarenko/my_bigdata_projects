import time
import pandas as pd
import requests

from bs4 import BeautifulSoup

# HTTP request headers to mimic a real browser visit
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}

# Configuration dictionary to manage headers, delay between requests,
# max retry attempts for failed requests, and HTTP statuses that trigger retries
CONFIG = {
    "headers": HEADERS,
    "delay": 3,
    "max_retries": 3,
    "retry_statuses": [429, 500, 502, 503, 504]
}


class ProductParser:
    """
    A class responsible for parsing product data from a website that supports pagination.
    It scrapes product name, image link, and price from multiple pages.
    """

    @staticmethod
    def parse_web_scraping_with_paginator(base_url, max_pages=3, delay=CONFIG["delay"]):
        all_products_data = pd.DataFrame()
        """
        Parses product data from multiple pages of the given base URL.

        Args:
            base_url (str): The base URL of the product listing page.
            max_pages (int): Maximum number of pages to parse.
            delay (int): Delay in seconds between requests to avoid overloading the server.

        Returns:
            pd.DataFrame: A DataFrame containing all parsed product data.
        """

        for page in range(1, max_pages + 1):

            try:
                # Construct the URL for the current page
                url = f"{base_url}/?page={page}"

                response = requests.get(url, headers=CONFIG["headers"])

                # Check response status and retry if necessary
                fetch_with_retries(response)

                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, "html.parser")

                # Find all product containers on the page
                products_wrap = soup.findAll("div", class_="products-wrap")

                # Iterate through each product container
                for product_wrap in products_wrap:

                    products = product_wrap.findAll("div", class_="row product")
                    # Extract details for each product
                    for product in products:
                        if product:

                            # Extract product image URL
                            img_product = product.find("div", class_="col-2 thumbnail")
                            img_tag = img_product.find("img") if img_product else "No img was finding."
                            product_img_link = img_tag["src"] if img_tag else None

                            # Extract product name
                            mb0_name = product.find("h3", class_="mb-0")
                            product_name = mb0_name.text.strip() if mb0_name else "No name was finding."

                            # Extract product name
                            price_tag = product.find("div", class_="col-2 price-wrap")
                            product_price = price_tag.text.strip() if price_tag else "No price was finding."

                            # Extract product name
                            temp_df = pd.DataFrame([{
                                "Product name": product_name,
                                "Image link": product_img_link,
                                "Price": product_price
                            }])

                            # Append the current product data to the main DataFrame
                            all_products_data = pd.concat([all_products_data, temp_df], ignore_index=True)

                    print(f"Page nr {page} produced ({len(products)} products)")
                    time.sleep(delay)

            except Exception as e:
                print(f"Page parsing error {page}: {e}")
                continue

        return all_products_data


def fetch_with_retries(response) -> None:
    """
    Checks the HTTP response status and retries the request if the status is in retry_statuses.
    Raises an exception if the maximum number of retries is exceeded without success.
    """
    for attempt in range(1, CONFIG["max_retries"]):
        # Status check
        if response.status_code in CONFIG["retry_statuses"]:
            print(f"Attempt {attempt + 1}: bad status {response.status_code}, retrying...")
            time.sleep(CONFIG["delay"])
            continue
        else:
            break  # if connect is success go out from cycle

    # If the response status code indicates a retryable error
    if response.status_code in CONFIG["retry_statuses"]:
        raise requests.exceptions.RequestException(
            f"Failed after {CONFIG['max_retries']} attempts (status {response.status_code})"
        )


if __name__ == "__main__":
    url = "https://web-scraping.dev/products"
    products_data = ProductParser.parse_web_scraping_with_paginator(url, max_pages=3)
    products_data.to_csv("web-scraping_products.csv", index=False, encoding="utf-8-sig")
    print(f"Parsed {len(products_data)} products")
    print(products_data.head())
