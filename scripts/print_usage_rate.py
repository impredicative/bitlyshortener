"""Print the used percentage."""
import os
import time

from bitlyshortener import Shortener, config  # pylint: disable=import-error

config.configure_logging()

# pylint: disable=invalid-name
TOKENS = os.environ["BITLY_TOKENS"].strip().split(",")
print(f"Number of tokens is {len(TOKENS)}.")

try:
    shortener = Shortener(tokens=TOKENS)
    usage = shortener.usage()
    print(f"Used percentage is {usage:.1%}.")
except Exception:
    time.sleep(0.01)  # Delay for longs to flush.
    raise
