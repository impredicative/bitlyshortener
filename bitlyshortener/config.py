"""Package configuration."""
import logging.config
from pathlib import Path


def configure_logging() -> None:
    """Configure logging."""
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug("Logging is configured.")


API_BASE_URL = "https://api-ssl.bitly.com/v4"  # Ref: https://dev.bitly.com/api-reference
API_URL_BITLINKS = f"{API_BASE_URL}/bitlinks"  # Ref: https://dev.bitly.com/api-reference#createFullBitlink
API_URL_ORGANIZATIONS = f"{API_BASE_URL}/organizations"  # Ref: https://dev.bitly.com/api-reference#getOrganizations
API_URL_FORMAT_ORGANIZATION_LIMITS = f"{API_BASE_URL}/organizations/{{organization_guid}}/plan_limits"  # Ref: https://dev.bitly.com/api-reference#getPlanLimits
API_URL_SHORTEN = f"{API_BASE_URL}/shorten"  # Ref: https://dev.bitly.com/api-reference#createBitlink
DEFAULT_CACHE_SIZE = 256
KNOWN_SHORT_DOMAINS = {"bit.ly", "j.mp"}
MAX_WORKERS = 32
MAX_WORKERS_PER_TOKEN = 5  # Ref: https://dev.bitly.com/v4/#section/Rate-Limiting
PACKAGE_NAME = Path(__file__).parent.stem
REQUEST_TIMEOUT = 3
TEST_API_ON_INIT = False
TEST_LONG_URL = "https://python.org/"
USAGE_CACHE_TIME = 3600

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    "version": 1,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s %(thread)x-%(threadName)s:%(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s",  # pylint: disable=line-too-long
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {PACKAGE_NAME: {"level": "DEBUG", "handlers": ["console"], "propagate": False}},
}
