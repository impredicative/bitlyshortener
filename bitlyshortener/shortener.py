from functools import lru_cache
import logging
import random
from typing import List

from . import config, exc
from .util import BytesIntEncoder

import requests

config.configure_logging()

log = logging.getLogger(__name__)


class Shortener:
    def __init__(self, *, tokens: List[str], max_cache_size: int = config.MIN_CACHE_SIZE):
        self._tokens = tokens
        self._max_cache_size = max_cache_size
        self._check_args()

        self._bytes_int_encoder = BytesIntEncoder()
        self._long_url_to_int_id = lru_cache(maxsize=self._max_cache_size)(self._long_url_to_int_id)  # type: ignore  # Instance level cache
        self._test()

    def _check_args(self):
        tokens = self._tokens
        if not (tokens and isinstance(tokens, list) and all(isinstance(token, str) for token in tokens)):
            raise exc.ArgsError('Tokens must be a list of one or more strings.')  # Tokens must not be logged.

        max_cache_size = self._max_cache_size
        if not isinstance(max_cache_size, int) or (max_cache_size < config.MIN_CACHE_SIZE):
            raise exc.ArgsError(f'Max cache size must be an integer ≥{config.MIN_CACHE_SIZE}, but it is '
                                f'{max_cache_size}.')

    def _int_id_to_short_url(self, url_id: int) -> str:
        url_id = self._bytes_int_encoder.decode(url_id).decode()
        short_url = f'https://j.mp/{url_id}'
        return short_url

    def _long_url_to_int_id(self, long_url: str) -> int:
        """
        :param url:
        :return:
        Can raise: requests.exceptions.HTTPError, requests.exceptions.ConnectTimeout
        """
        tokens = random.sample(self._tokens, len(self._tokens))
        endpoints = config.API_URL_BITLINKS, config.API_URL_SHORTEN  # Used in reverse order.
        attempts = [(endpoint, token) for endpoint in endpoints for token in tokens]
        num_max_attempts = len(attempts)
        while attempts:
            endpoint, token = attempts.pop()
            num_attempt = num_max_attempts - len(attempts)
            endpoint_desc = f'endpoint /{endpoint.rpartition("/")[-1]}'
            response_desc = f'response from {endpoint_desc} using token starting with ' \
                            f'{token[:4]} for long URL {long_url} in attempt {num_attempt} of {num_max_attempts}'
            try:
                log.debug('Requesting %s.', response_desc)
                response = requests.post(url=endpoint, json={'long_url': long_url}, allow_redirects=False,
                                         headers={'Authorization': f'Bearer {token}'}, timeout=config.REQUEST_TIMEOUT)
                response_json = response.json()
                log.debug('Received %s having status code %s with short URL %s.',
                          response_desc, response.status_code, response_json['link'])
                response.raise_for_status()
                break
            except (requests.HTTPError, requests.ConnectTimeout) as exception:
                log.warning('Error receiving %s. f this is due to token-specific rate limit, consider using more '
                            'tokens, although an IP rate limit nevertheless applies. The exception is: %s: %s',
                            response_desc, exception.__class__.__qualname__, exception)
                if isinstance(exception, requests.HTTPError):
                    log.info('Response text is: %s', response.text)
                if attempts:
                    continue
                else:
                    log.error('Exhausted all %s attempts requesting response from %s for long URL %s.',
                              num_max_attempts, endpoint_desc, long_url)
                    raise
        assert response.status_code in (200, 201)  # Investigational.
        url_id = response_json['link'].rpartition('/')[-1]
        url_id = self._bytes_int_encoder.encode(url_id.encode())
        return url_id

    def _test(self):
        long_url = config.TEST_LONG_URL
        log.debug('Testing API for long URL %s.', long_url)
        short_url = self.shorten_url(long_url)
        log.debug('Tested API for long URL %s. Received short URL %s.', long_url, short_url)

    def shorten_url(self, long_url: str) -> str:
        url_id = self._long_url_to_int_id(long_url)
        short_url = self._int_id_to_short_url(url_id)
        log.debug('Returning short URL %s for long URL %s.', short_url, long_url)
        return short_url

    def shorten_urls(self, long_urls: List[str]) -> List[str]:  # TODO: Use concurrency.
        short_urls = [self.shorten_url(long_url) for long_url in long_urls]
        return short_urls
