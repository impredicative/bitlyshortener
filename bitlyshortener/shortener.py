from typing import List, Optional


class Shortener:
    def __init__(self, *, max_cache_len: Optional[int] = 1024, tokens: List[str]):
        self._max_cache_len = max_cache_len
        self._tokens = tokens

    def shorten(self, urls: List[str]) -> List[str]:
        return urls
