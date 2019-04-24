import logging.config
from pathlib import Path


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


API_URL_BITLINKS = 'https://api-ssl.bitly.com/v4/bitlinks'  # Ref: https://dev.bitly.com/v4/#operation/createFullBitlink
API_URL_SHORTEN = 'https://api-ssl.bitly.com/v4/shorten'  # Ref: https://dev.bitly.com/v4/#operation/createBitlink
DEFAULT_CACHE_SIZE = 2048
KNOWN_SHORT_DOMAINS = {'bit.ly', 'j.mp'}
MAX_WORKERS = 32
MAX_WORKERS_PER_TOKEN = 5  # Ref: https://dev.bitly.com/v4/#section/Rate-Limiting
PACKAGE_NAME = Path(__file__).parent.stem
REQUEST_TIMEOUT = 3
TEST_API_ON_INIT = False
TEST_LONG_URL = 'https://python.org/'

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(thread)x-%(threadName)s:%(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        PACKAGE_NAME: {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
