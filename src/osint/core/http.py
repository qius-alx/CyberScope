# src/osint/core/http.py
import requests
import requests_cache
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

from osint.core.config import settings
from osint.core.logger import logger


class HttpClient:
    def __init__(self, use_cache: bool = True, use_tor: bool = False):
        if use_cache:
            requests_cache.install_cache(
                "osint_cache",
                backend="sqlite",
                expire_after=3600,  # Cache expires after 1 hour
                allowable_codes=[200],
            )
            logger.info("HTTP response caching is enabled.")

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

        proxies = {}
        if use_tor:
            if settings.tor_proxy:
                proxies["http"] = settings.tor_proxy
                proxies["https"] = settings.tor_proxy
                logger.info(f"Using Tor proxy: {settings.tor_proxy}")
            else:
                logger.warning("Tor is requested, but no tor_proxy is configured.")
        elif settings.http_proxy:
            proxies["http"] = settings.http_proxy
            proxies["https"] = settings.http_proxy
            logger.info(f"Using HTTP proxy: {settings.http_proxy}")

        if proxies:
            self.session.proxies.update(proxies)

    @retry(
        stop=stop_after_attempt(settings.http_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True,
    )
    def get(self, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", settings.http_timeout)
        try:
            response = self.session.get(url, **kwargs)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP GET request failed for {url}: {e}")
            raise
        except RetryError as e:
            logger.error(f"HTTP GET request failed after multiple retries for {url}: {e}")
            raise

    # You can add other methods like post, put, etc. following the same pattern.
    # For now, GET is sufficient for most OSINT tasks.


# Global http client instance
http_client = HttpClient()
