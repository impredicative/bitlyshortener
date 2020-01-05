# Concurrent-only shortening (untested):
def shorten_urls(self, long_urls: List[str]) -> List[str]:
    self._check_long_urls(long_urls)
    num_long_urls = len(long_urls)
    num_workers = min(num_long_urls, self._max_workers)
    log.debug("Retrieving %s short URLs using %s workers.", num_long_urls, num_workers)
    start_time = time.monotonic()
    short_urls = list(self._executor.map(self._shorten_url, long_urls))
    time_used = time.monotonic() - start_time
    num_short_urls = len(short_urls)
    assert num_long_urls == num_short_urls
    urls_per_second = num_short_urls / time_used
    log.info(
        "Retrieved %s short URLs using %s workers in %.1fs at a rate of %.0f/s. %s",
        num_short_urls,
        num_workers,
        time_used,
        urls_per_second,
        self._cache_state(),
    )
    return short_urls
