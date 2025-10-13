BOT_NAME = "quotesproj"
SPIDER_MODULES = ["quotesproj.spiders"]
NEWSPIDER_MODULE = "quotesproj.spiders"

# Disable obeying robots.txt — allows crawling all pages
ROBOTSTXT_OBEY = False

# Control concurrency
CONCURRENT_REQUESTS = 8                 # total number of parallel requests
CONCURRENT_REQUESTS_PER_DOMAIN = 4      # per domain limit
DOWNLOAD_DELAY = 0                      # no artificial delay
DOWNLOAD_TIMEOUT = 30                   # timeout for each request

# Enable AutoThrottle — automatic speed control based on server load
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Retry failed requests (e.g. 429 Too Many Requests, 5xx errors)
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [429, 500, 502, 503, 504]

# Logging configuration
LOG_LEVEL = "DEBUG"
STATS_DUMP = True
LOGSTATS_INTERVAL = 10

# Export encoding for output files (if any)
FEED_EXPORT_ENCODING = "utf-8"

# Default headers — make requests look like a browser
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Middleware chain (custom + built-in)
DOWNLOADER_MIDDLEWARES = {
    "quotesproj.middlewares.RandomUserAgent": 400,                 # random User-Agent generator
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,     # retry failed requests
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,  # disable default UA
}

# Pipeline for saving cleaned items to PostgreSQL
ITEM_PIPELINES = {
    "quotesproj.pipelines.DatabasePipeline": 300,
}

# Disable cookies and Telnet console
COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False