import random
import time
import logging
from fake_useragent import UserAgent
from scrapy.http import Request, Response

logger = logging.getLogger(__name__)

# Base class for all custom middlewares
class BaseMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        # Required Scrapy hook for middleware initialization
        return cls()


# Middleware for rotating User-Agent and handling retry logic
class RandomUserAgent(BaseMiddleware):

    BAD_STATUSES = {429, 500, 502, 503, 504}  # HTTP codes that trigger retry

    def __init__(self, delay_range=(1.0, 3.0)):
        # Initialize random User-Agent generator
        self.ua = UserAgent()
        self.delay_range = delay_range  # range for random retry delay

    def _random_ua(self):
        # Generate random User-Agent; fallback to static ones if service fails
        try:
            return self.ua.random
        except Exception:
            # Fallback in case fake-useragent API is unavailable
            return random.choice([
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
            ])

    def process_request(self, request: Request, spider):
        # Assign a random User-Agent to each outgoing request
        ua = self._random_ua()
        request.headers["User-Agent"] = ua
        logger.debug(f"[UA] Using User-Agent: {ua}")

    def process_response(self, request: Request, response: Response, spider):
        # Handle retry logic for specific HTTP error statuses
        if response.status in self.BAD_STATUSES:
            delay = random.uniform(*self.delay_range)
            logger.warning(f"[Retry] Status {response.status} for {response.url} — waiting {delay:.1f}s and retrying...")
            time.sleep(delay)

            # Rebuild the request with a new User-Agent and retry it
            new_request = request.replace(dont_filter=True)
            new_request.headers["User-Agent"] = self._random_ua()
            return new_request

        # Return valid response to Scrapy
        return response