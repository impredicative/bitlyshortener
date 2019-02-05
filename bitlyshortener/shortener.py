import concurrent.futures
from functools import lru_cache
import logging
import random
import time
import threading
from typing import List

from . import config, exc
from .util import BytesIntEncoder

import requests

log = logging.getLogger(__name__)


class Shortener:
    def __init__(self, *, tokens: List[str], max_cache_size: int = config.MIN_CACHE_SIZE):
        self._tokens = sorted(set(tokens))  # Sorted for subsequent reproducible randomization.
        self._max_cache_size = max_cache_size
        self._check_args()

        self._bytes_int_encoder = BytesIntEncoder()
        self._long_url_to_int_id = lru_cache(maxsize=self._max_cache_size)(self._long_url_to_int_id)  # type: ignore  # Instance level cache
        self._init_executor()
        if config.TEST_API_ON_INIT:
            self._test()

    def _cache_state(self) -> str:
        cache_info = self._long_url_to_int_id.cache_info()
        calls = cache_info.hits + cache_info.misses
        hit_percentage = ((100 * cache_info.hits) / calls) if (calls != 0) else 0
        size_percentage = (100 * cache_info.currsize) / cache_info.maxsize
        cache_state = f'Cache state is: hits={cache_info.hits}, currsize={cache_info.currsize}, ' \
                      f'hit_rate={hit_percentage:.0f}%, size_rate={size_percentage:.0f}%'
        return cache_state

    def _check_args(self) -> None:
        tokens = self._tokens
        if not (tokens and isinstance(tokens, list) and all(isinstance(token, str) for token in tokens) and
                (len(tokens) == len(set(tokens)))):
            raise exc.ArgsError('Tokens must be a list of one or more unique strings.')  # Tokens must not be logged.
        log.debug('Number of unique tokens is %s.', len(tokens))

        max_cache_size = self._max_cache_size
        if (not isinstance(max_cache_size, int)) or (max_cache_size < config.MIN_CACHE_SIZE):
            raise exc.ArgsError(f'Max cache size must be an integer ≥{config.MIN_CACHE_SIZE}, but it is '
                                f'{max_cache_size}.')
        log.debug('Max cache size is %s.', max_cache_size)

    def _init_requests_session(self) -> None:
        self._thread_local.session = requests.Session()
        log.debug('Initialized requests session having object ID %x.', id(self._thread_local.session))

    def _init_executor(self) -> None:
        self._max_workers = min(config.MAX_WORKERS, len(self._tokens) * config.MAX_WORKERS_PER_TOKEN)
        log.debug('Max number of worker threads is %s.', self._max_workers)
        self._thread_local = threading.local()
        self._init_requests_session()  # For conditional non-parallel execution.
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers,
                                                               thread_name_prefix='Requester',
                                                               initializer=self._init_requests_session)
        log.debug('Initialized thread pool executor.')

    def _int_id_to_short_url(self, url_id: int) -> str:
        url_id_ = self._bytes_int_encoder.decode(url_id).decode()
        short_url = f'https://j.mp/{url_id_}'
        return short_url

    def _long_url_to_int_id(self, long_url: str) -> int:  # type: ignore
        # Can raise: requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout
        long_url = long_url.strip()
        if len(self._tokens) > 1:
            randomizer = random.Random(long_url)  # For reproducible randomization.
            # Reproducibility of randomization is useful so as to prevent creating the same short URL under multiple
            # tokens, as this counts toward a monthly creation quota.
            tokens = randomizer.sample(self._tokens, len(self._tokens))
        else:
            tokens = self._tokens
        endpoints = config.API_URL_BITLINKS, config.API_URL_SHORTEN  # Specified in reverse order due to pop().
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
                start_time = time.monotonic()
                response = self._thread_local.session.post(url=endpoint, json={'long_url': long_url},
                                                           allow_redirects=False, timeout=config.REQUEST_TIMEOUT,
                                                           headers={'Authorization': f'Bearer {token}'})
                time_used = time.monotonic() - start_time
                response_json = response.json()
                short_url_desc = f'with link {response_json["link"]}' if ('link' in response_json) else 'with no link'
                log.debug('Received %s having status code %s %s in %.1fs.',
                          response_desc, response.status_code, short_url_desc, time_used)
                response.raise_for_status()
                break
            except (requests.HTTPError, requests.ConnectionError, requests.ConnectTimeout) as exception:  # type: ignore
                exception_desc = f'The exception is: {exception.__class__.__qualname__}: {exception}'
                if isinstance(exception, (requests.ConnectTimeout, requests.ConnectionError)):  # type: ignore
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

    def _shorten_url(self, long_url: str) -> str:
        url_id = self._long_url_to_int_id(long_url)
        short_url = self._int_id_to_short_url(url_id)
        log.debug('Returning short URL %s for long URL %s.', short_url, long_url)
        return short_url

    def _test(self) -> None:
        long_url = config.TEST_LONG_URL
        log.debug('Testing API for long URL %s.', long_url)
        short_url = self.shorten_urls([long_url])
        log.debug('Tested API for long URL %s. Received short URL %s.', long_url, short_url)

    def shorten_urls(self, long_urls: List[str]) -> List[str]:
        num_long_urls = len(long_urls)
        if len(set(long_urls)) > 1:
            strategy_desc = 'Concurrently'
            num_workers = min(num_long_urls, self._max_workers)
            resource_desc = f' using up to {num_workers} worker threads'
            mapper = self._executor.map
        else:
            strategy_desc = 'Serially'
            resource_desc = ''
            mapper = map  # type: ignore
        log.debug('%s retrieving %s short URLs%s.', strategy_desc, num_long_urls, resource_desc)
        start_time = time.monotonic()
        short_urls = list(mapper(self._shorten_url, long_urls))
        time_used = time.monotonic() - start_time
        num_short_urls = len(short_urls)
        assert num_long_urls == num_short_urls
        urls_per_second = num_short_urls / time_used
        log.info('%s retrieved %s short URLs in %.1fs at a rate of %.0f/s. %s', strategy_desc, num_short_urls,
                 time_used, urls_per_second, self._cache_state())
        return short_urls
