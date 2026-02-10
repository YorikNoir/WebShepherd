"""
URL Fetcher - Handles async HTTP requests with safety constraints
"""
import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)


class URLFetcher:
    """Async URL fetcher with safety limits"""

    def __init__(self):
        self.timeout = httpx.Timeout(settings.REQUEST_TIMEOUT)
        self.max_size = settings.MAX_HTML_SIZE_MB * 1024 * 1024  # Convert MB to bytes
        self.max_redirects = settings.MAX_REDIRECTS

    async def fetch(self, url: str) -> str:
        """
        Fetch HTML content from URL

        Args:
            url: URL to fetch

        Returns:
            HTML content as string

        Raises:
            httpx.HTTPError: On HTTP errors
            ValueError: If content too large or invalid
        """
        headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            max_redirects=self.max_redirects
        ) as client:
            try:
                logger.info(f"Fetching URL: {url}")
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    raise ValueError(f"Invalid content type: {content_type}. Expected text/html")

                # Check content size
                content_length = len(response.content)
                if content_length > self.max_size:
                    raise ValueError(
                        f"Content too large: {content_length / 1024 / 1024:.1f} MB "
                        f"(max: {settings.MAX_HTML_SIZE_MB} MB)"
                    )

                logger.info(f"Successfully fetched {content_length / 1024:.1f} KB from {url}")
                return response.text

            except httpx.TimeoutException:
                logger.error(f"Timeout fetching {url}")
                raise ValueError(f"Request timeout after {settings.REQUEST_TIMEOUT} seconds")

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for {url}")
                raise ValueError(f"HTTP {e.response.status_code}: {e.response.reason_phrase}")

            except httpx.RequestError as e:
                logger.error(f"Request error for {url}: {str(e)}")
                raise ValueError(f"Failed to fetch URL: {str(e)}")
