from functools import lru_cache
import random
from typing import List, Optional

from .config import API_URL_SHORTEN, REQUEST_TIMEOUT
from .util import BytesIntEncoder

import requests


class Shortener:
    def __init__(self, *, max_cache_size: Optional[int] = 1024, tokens: List[str]):
        self._tokens = tokens
        self._bytes_int_encoder = BytesIntEncoder()
        self._long_url_to_int_id = lru_cache(maxsize=max_cache_size)(self._long_url_to_int_id)  # type: ignore  # Instance level cache

    def _long_url_to_int_id(self, long_url: str) -> int:
        """
        :param url:
        :return:
        Can raise: requests.exceptions.HTTPError, requests.exceptions.ConnectTimeout
        """
        tokens = random.sample(self._tokens, len(self._tokens))
        while tokens:
            token = tokens.pop()
            try:
                response = requests.post(url=API_URL_SHORTEN, json={'long_url': long_url}, allow_redirects=False,
                                         headers={'Authorization': f'Bearer {token}'}, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                break
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectTimeout) as exc:
                if tokens:
                    # TODO: Log exc as warning.
                    continue
                else:
                    # TODO: Log exc as error.
                    raise
        assert response.status_code in (200, 201)
        url_id = response.json()['link'].rpartition('/')[-1]
        url_id = self._bytes_int_encoder.encode(url_id.encode())
        return url_id

    def _int_id_to_short_url(self, url_id: int) -> str:
        url_id = self._bytes_int_encoder.decode(url_id).decode()
        short_url = f'https://j.mp/{url_id}'
        return short_url

    def shorten_url(self, long_url: str) -> str:
        url_id = self._long_url_to_int_id(long_url)
        short_url = self._int_id_to_short_url(url_id)
        return short_url

    def shorten_urls(self, long_urls: List[str]) -> List[str]:
        short_urls = [self.shorten_url(long_url) for long_url in long_urls]
        return short_urls
