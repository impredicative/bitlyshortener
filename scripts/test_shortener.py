import os
import time

from bitlyshortener import Shortener

tokens = os.getenv('BITLY_TOKENS').strip().split(',')

try:
    shortener = Shortener(tokens=tokens)

    # print(shortener.shorten_urls(['https://cnn.com/']))
    # print(shortener.shorten_urls(['https://cnn.com/']))

    urls = ['https://paperswithcode.com/latest', 'https://towardsdatascience.com/machine-learning/home',
            'https://research.fb.com/publications/']
    print(shortener.shorten_urls(urls))
    print(shortener.shorten_urls(urls[::-1]))

except Exception:
    time.sleep(0.01)  # Delay for longs to flush.
    raise
