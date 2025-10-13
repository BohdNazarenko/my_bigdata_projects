import time
from datetime import datetime

import scrapy
from scrapy.http import HtmlResponse
from ..items import QuoteItem

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class QuotesScrollSpider(scrapy.Spider):
    name = "quotes_scroll"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/scroll"]  # динамический сценарий

    # --- Selenium helpers ---
    def _build_driver(self):
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        svc = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=svc, options=opts)

    def _scroll_to_bottom(self, driver, pause=0.7, max_stuck=2):
        last_h = driver.execute_script("return document.body.scrollHeight")
        stuck = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                stuck += 1
                if stuck >= max_stuck:
                    break
            else:
                stuck = 0
                last_h = new_h

    def _render_with_selenium(self, url: str) -> HtmlResponse:
        d = self._build_driver()
        try:
            d.get(url)
            WebDriverWait(d, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".quote")))
            if "/scroll" in url:
                self._scroll_to_bottom(d, pause=0.7, max_stuck=2)
                time.sleep(0.5)
            html = d.page_source
            return HtmlResponse(url=url, body=html.encode("utf-8"), encoding="utf-8")
        finally:
            d.quit()

    # --- entry ---
    def start_requests(self):
        for url in self.start_urls:
            resp = self._render_with_selenium(url)
            yield from self.parse(resp)

        # второй сценарий: классическая пагинация (статичная)
        yield scrapy.Request("https://quotes.toscrape.com/", callback=self.parse_static)

    # --- parse dynamic (scroll) ---
    def parse(self, response):
        for q in response.css(".quote"):
            item = QuoteItem()
            item["url"] = response.url
            item["parsed_at"] = datetime.utcnow().isoformat()
            item["text"] = q.css(".text::text").get()
            item["author"] = q.css(".author::text").get()
            item["tags"] = q.css(".tag::text").getall()
            author_url = response.urljoin(q.css("span a::attr(href)").get())
            item["author_url"] = author_url

            # вложенные данные со страницы автора
            yield scrapy.Request(author_url, callback=self.parse_author, cb_kwargs={"item": item})

    # --- parse static with "Next" pagination ---
    def parse_static(self, response):
        for q in response.css(".quote"):
            item = QuoteItem()
            item["url"] = response.url
            item["parsed_at"] = datetime.utcnow().isoformat()
            item["text"] = q.css(".text::text").get()
            item["author"] = q.css(".author::text").get()
            item["tags"] = q.css(".tag::text").getall()
            author_url = response.urljoin(q.css("span a::attr(href)").get())
            item["author_url"] = author_url
            yield scrapy.Request(author_url, callback=self.parse_author, cb_kwargs={"item": item})

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse_static)

    def parse_author(self, response, item: QuoteItem):
        item["author_born_date"] = response.css(".author-born-date::text").get()
        item["author_born_location"] = response.css(".author-born-location::text").get()
        item["author_description"] = " ".join(response.css(".author-description::text").getall()).strip()
        yield item