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
        self._session = requests.Session()
        if config.TEST_API_ON_INIT:
            self._test()

    def _check_args(self) -> None:
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
        # Can raise: requests.HTTPError, requests.ConnectTimeout
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
                response = self._session.post(url=endpoint, json={'long_url': long_url}, allow_redirects=False,
                                              headers={'Authorization': f'Bearer {token}'},
                                              timeout=config.REQUEST_TIMEOUT)
                response_json = response.json()
                short_url_desc = f'with link {response_json["link"]}' if ('link' in response_json) else 'with no link'
                log.debug('Received %s having status code %s %s.',
                          response_desc, response.status_code, short_url_desc)
                response.raise_for_status()
                break
            except (requests.HTTPError, requests.ConnectTimeout) as exception:
                exception_desc = f'The exception is: {exception.__class__.__qualname__}: {exception}'
                if isinstance(exception, requests.ConnectTimeout):
                    log.warning('Error receiving %s. %s', response_desc, exception_desc)
                elif isinstance(exception, requests.HTTPError):
                    log.warning('Error receiving %s. If this is due to token-specific rate limit, consider using more '
                                'tokens, although an IP rate limit nevertheless applies. The response status code is '
                                '%s and text is %s. %s',
                                response_desc, response.status_code, response.text, exception_desc)
                    if response.status_code == 400:  # Bad request.
                        raise
                if not attempts:
                    log.error('Exhausted all %s attempts requesting response from %s for long URL %s.',
                              num_max_attempts, endpoint_desc, long_url)
                    raise
        assert response.status_code in (200, 201)  # Investigational.
        url_id = response_json['link'].rpartition('/')[-1]
        url_id = self._bytes_int_encoder.encode(url_id.encode())
        return url_id

    def _test(self) -> None:
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
        log.debug('Retrieving %s short URLs.', len(long_urls))
        short_urls = [self.shorten_url(long_url) for long_url in long_urls]
        log.info('Returning %s short URLs.', len(short_urls))
        return short_urls
