import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.livelib.ru/genre/Классическая-литература")
print(response.text)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}

# Великая и ужасная кодировка
# При последней проверки работоспособности парсера сайтом принималась именно такая
# Эквивалентна https://www.livelib.ru/genre/Классическая-литература/
url = ("https://www.livelib.ru/genre/%D0%9A%D0%BB%D0%B0%D1%81%D1%81%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F-%"
       "D0%BB%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0")
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")


print(soup.text)


first_book = soup.find("div", class_="book-item__inner")

# Пробуем взять первую книгу
if first_book:

    # Название и автор
    title_elem = first_book.find("a", class_="book-item__title")
    title = title_elem.text.strip() if title_elem else "Название не указано"

    author_elem = first_book.find("a", class_="book-item__author")
    author = author_elem.text.strip() if author_elem else "Автор не указан"

    # Рейтинг
    rating_tag = first_book.find("div", class_="rating-value")
    rating = rating_tag.text.strip() if rating_tag else "Нет рейтинга"

    # Статистика
    stats = first_book.find_all("a", class_=[
        "icon-added-grey", "icon-read-grey", "icon-review-grey", "icon-quote-grey"
    ])
    stats_values = [stat.text.strip() for stat in stats] if stats else []
    stats_values += ["0"] * (4 - len(stats_values))


# Временный DataFrame для текущей книги
temp_df = pd.DataFrame([{
    "Название": title,
    "Автор": author,
    "Рейтинг": rating,
    "Прочитали": stats_values[0],
    "Хотят прочитать": stats_values[1],
    "Рецензии": stats_values[2],
    "Цитаты": stats_values[3]
}])

def parse_livelib_with_pagination(base_url, max_pages=5, delay=2):
    # Датафрейм, куда будем собирать все страницы
    all_data = pd.DataFrame()

    for page in range(1, max_pages + 1):
        try:
            # Формируем ссылку на страницу
            url = f"{base_url}/listview/biglist/~{page}"

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            books = soup.find_all("div", class_="book-item__inner")

            for book in books:
                title_elem = book.find("a", class_="book-item__title")
                title = title_elem.text.strip() if title_elem else "Название не указано"

                author_elem = book.find("a", class_="book-item__author")
                author = author_elem.text.strip() if author_elem else "Автор не указан"

                rating_tag = book.find("div", class_="rating-value")
                rating = rating_tag.text.strip() if rating_tag else "Нет рейтинга"

                stats = book.find_all("a", class_=[
                    "icon-added-grey", "icon-read-grey", "icon-review-grey", "icon-quote-grey"
                ])
                stats_values = [stat.text.strip() for stat in stats] if stats else []
                stats_values += ["0"] * (4 - len(stats_values))

                temp_df = pd.DataFrame([{
                    "Название": title,
                    "Автор": author,
                    "Рейтинг": rating,
                    "Прочитали": stats_values[0],
                    "Хотят прочитать": stats_values[1],
                    "Рецензии": stats_values[2],
                    "Цитаты": stats_values[3]
                }])

                all_data = pd.concat([all_data, temp_df], ignore_index=True)

            print(f"Страница {page} обработана ({len(books)} книг)")
            time.sleep(delay)

        except Exception as e:
            print(f"Ошибка при парсинге страницы {page}: {e}")
            continue

    return all_data



base_url = "https://www.livelib.ru/genre/%D0%9A%D0%BB%D0%B0%D1%81%D1%81%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F-%D0%BB%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0"
books_data = parse_livelib_with_pagination(base_url, max_pages=11)

books_data.to_csv("livelib_books.csv", index=False, encoding="utf-8-sig")

print(f"Спаршено {len(books_data)} книг")
print(books_data.head())
















