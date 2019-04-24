import concurrent.futures
from functools import _CacheInfo, lru_cache
import logging
import random
import time
import threading
from typing import Dict, List, Sequence, Set, Union
from urllib.parse import urlparse

from . import config, exc
from .util import BytesIntEncoder

import requests

log = logging.getLogger(__name__)


class Shortener:
    def __init__(self, *, tokens: Sequence[str], max_cache_size: int = config.DEFAULT_CACHE_SIZE):
        self._tokens = sorted(set(tokens))  # Sorted for subsequent reproducible randomization.
        self._max_cache_size = max_cache_size
        self._check_args()

        self._bytes_int_encoder = BytesIntEncoder()
        self._long_url_to_int_id = lru_cache(maxsize=self._max_cache_size)(self._long_url_to_int_id)  # type: ignore  # Instance level cache
        self._init_thread_id = threading.get_ident()
        self._init_executor()
        if config.TEST_API_ON_INIT:
            self._test()

    def _cache_state(self) -> str:
        cache_info = self._long_url_to_int_id.cache_info()
        calls = cache_info.hits + cache_info.misses
        hit_percentage = ((100 * cache_info.hits) / calls) if (calls != 0) else 0
        size_percentage = ((100 * cache_info.currsize) / cache_info.maxsize) if cache_info.maxsize else 100
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
        if (not isinstance(max_cache_size, int)) or (max_cache_size < 0):
            raise exc.ArgsError(f'Max cache size must be an integer ≥0, but it is {max_cache_size}.')
        log.debug('Max cache size is %s.', max_cache_size)

    def _init_requests_session(self) -> None:
        self._thread_local.session_post = requests.Session()
        self._thread_local.session_head = requests.Session()
        log.debug('Initialized requests sessions.')

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

    @staticmethod
    def _is_known_short_url(url: str) -> bool:
        result = urlparse(url)
        return (result.netloc in config.KNOWN_SHORT_DOMAINS) and (result.scheme in {'https', 'http'})

    def _lengthen_url(self, short_url: str) -> str:
        # Can raise: exc.RequestError
        short_url = short_url.strip()
        log.debug('Requesting long URL for short URL %s.', short_url)
        try:
            start_time = time.monotonic()
            response = self._thread_local.session_head.head(short_url, allow_redirects=False,
                                                            timeout=config.REQUEST_TIMEOUT)
            time_used = time.monotonic() - start_time
            response.raise_for_status()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as exception:
            exc_desc = f'The error is: {exception.__class__.__qualname__}: {exception}'
            msg = f'Error receiving long URL for short URL {short_url}. {exc_desc}'
            raise exc.RequestError(msg) from None
        assert response.status_code == 301
        long_url = response.headers['Location']
        log.debug('Received long URL for short URL %s which is %s with status code %s in %.1fs.',
                  short_url, long_url, response.status_code, time_used)
        return long_url

    def _long_url_to_int_id(self, long_url: str) -> int:  # type: ignore
        # Can raise: exc.RequestError
        long_url = long_url.strip()
        if self._is_known_short_url(long_url):
            # Note: A preexisting Bitly link can use one of many domains, not just j.mp. It can also be
            # a custom link or not. A custom link cannot be encoded to an integer for caching. Such a link
            # must be validated and normalized.
            long_url = self._lengthen_url(long_url)
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
                response = self._thread_local.session_post.post(url=endpoint, json={'long_url': long_url},
                                                                allow_redirects=False, timeout=config.REQUEST_TIMEOUT,
                                                                headers={'Authorization': f'Bearer {token}'})
                time_used = time.monotonic() - start_time
                response_json = response.json()
                short_url_desc = f'with link {response_json["link"]}' if ('link' in response_json) else 'without link'
                log.debug('Received %s having status code %s %s in %.1fs.',
                          response_desc, response.status_code, short_url_desc, time_used)
                response.raise_for_status()
                break
            except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as exception:
                exc_desc = f'The error is: {exception.__class__.__qualname__}: {exception}'
                if isinstance(exception, (requests.Timeout, requests.ConnectionError)):
                    log.warning('Error receiving %s. %s', response_desc, exc_desc)
                elif isinstance(exception, requests.HTTPError):
                    if response.status_code == 400 and response_json['message'] == 'ALREADY_A_BITLY_LINK':
                        # Note: A preexisting Bitly link can use one of many domains, not just j.mp. It can also be
                        # a custom link or not. A custom link cannot be encoded to an integer for caching. Such a link
                        # must be validated and normalized.
                        actual_long_url = self._lengthen_url(long_url)
                        return self._long_url_to_int_id(actual_long_url)
                    log.warning('Error receiving %s. If this is due to token-specific rate limit, consider using more '
                                'tokens, although an IP rate limit nevertheless applies. The response status code is '
                                '%s and text is %s. %s',  # Still just a warning, and not an error yet.
                                response_desc, response.status_code, response.text, exc_desc)
                    if response.status_code == 400:
                        msg = f'The response status code is 400 and so the request will not be reattempted. {exc_desc}'
                        raise exc.RequestError(msg) from None
                if not attempts:
                    msg = f'Exhausted all {num_max_attempts} attempts requesting response from {num_max_attempts} ' \
                        f'for long URL {long_url}. {exc_desc}'
                    raise exc.RequestError(msg) from None
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

    @property
    def cache_info(self) -> Dict[str, _CacheInfo]:
        source = self._long_url_to_int_id
        return {source.__qualname__: source.cache_info()}  # type: ignore

    def shorten_urls(self, long_urls: Union[Sequence[str], Set[str]]) -> List[str]:
        num_long_urls = len(long_urls)
        if (len(set(long_urls)) > 1) or (threading.get_ident() != self._init_thread_id):
            strategy_desc = 'Concurrently'
            num_workers = min(num_long_urls, self._max_workers)
            resource_desc = f' using {num_workers} workers'
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
        log.info('%s retrieved %s short URLs%s in %.1fs at a rate of %.0f/s. %s', strategy_desc, num_short_urls,
                 resource_desc, time_used, urls_per_second, self._cache_state())
        return short_urls

    def shorten_urls_to_dict(self, long_urls: Sequence[str]) -> Dict[str, str]:
        long_urls = set(long_urls)
        short_urls = self.shorten_urls(long_urls)
        url_map = dict(zip(long_urls, short_urls))
        return url_map
