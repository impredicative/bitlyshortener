import os
import time

from bitlyshortener import Shortener

tokens = os.getenv('BITLY_TOKENS').strip().split(',')

try:
    shortener = Shortener(tokens=tokens)
except Exception:
    time.sleep(0.01)  # Delay for longs to flush.
    raise
