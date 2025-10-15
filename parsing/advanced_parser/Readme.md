The project demonstrates a complete ETL pipeline using the educational website `quotes.toscrape.com`.

## 1. How to Run the Project:

#### 1. Navigate to the project
`cd my_bigdata_projects/parsing/advanced_parser/quotes_spider`

#### 2. Activate virtual environment
`source .venv/bin/activate`     # macOS/Linux
`.venv\Scripts\activate`      # Windows PowerShell

#### 3. Install dependencies
`pip install -r requirements.txt`

#### 4. Start PostgreSQL (Docker)
`docker compose up -d`

#### 5. Create and configure .env file
`cp .env.example .env`

#### 6. Run the Scrapy spider
`scrapy crawl quotes_scroll`

#### 7. Run the Spark job
`python spark_jobs/quotes_raw_to_dwh.py`
or:
`spark-submit --packages org.postgresql:postgresql:42.7.4 spark_jobs/quotes_raw_to_dwh.py`


## 2. Module Overview

[quotes_scroll.py](quotes_spider/quotesproj/spiders/quotes_scroll.py) — Demonstrates both dynamic scraping (via Selenium scroll) and static pagination using Scrapy.

[middlewares.py](quotes_spider/quotesproj/middlewares.py) — Implements a RandomUserAgent middleware with retry and backoff for HTTP 429/5xx responses.

[pipelines.py](quotes_spider/quotesproj/pipelines.py) — SQLAlchemy pipeline — inserts quotes and performs UPSERTs for authors.

[models.py](quotes_spider/quotesproj/models.py) — ORM models for quotes and raw_authors tables.

[quotes_raw_to_dwh.py](quotes_spider/spark_jobs/quotes_raw_to_dwh.py) — Simple PySpark job to clean and flatten data into a warehouse table.









