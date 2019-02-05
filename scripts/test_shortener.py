import os
import time

from bitlyshortener import Shortener

tokens = os.getenv('BITLY_TOKENS').strip().split(',')

try:
    shortener = Shortener(tokens=tokens)
    print(shortener.shorten_urls(['https://cnn.com/']))
    print(shortener.shorten_urls(['https://cnn.com/']))
except Exception:
    time.sleep(0.01)  # Delay for longs to flush.
    raise
