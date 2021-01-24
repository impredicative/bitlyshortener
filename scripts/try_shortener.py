"""Try using the shortener."""
import os
import random
import time

from bitlyshortener import Shortener, config  # pylint: disable=import-error

config.configure_logging()

# pylint: disable=invalid-name
TOKENS = os.environ["BITLY_TOKENS"].strip().split(",")
URLs = [
    "https://arxiv.org/abs/1901.10500v2",
    "https://arxiv.org/abs/1901.08649v2",
    "https://arxiv.org/abs/1901.03162v2",
    "https://arxiv.org/abs/1812.05687v2",
    "https://arxiv.org/abs/1812.04608v2",
    "https://arxiv.org/abs/1812.01127v2",
    "https://arxiv.org/abs/1811.03742v2",
    "https://arxiv.org/abs/1810.07180v4",
    "https://arxiv.org/abs/1810.06544v2",
    "https://arxiv.org/abs/1809.10326v3",
    "https://arxiv.org/abs/1804.10938v5",
    "https://arxiv.org/abs/1604.05636v3",
    "https://arxiv.org/abs/1902.00506v1",
    "https://arxiv.org/abs/1902.00465v1",
    "https://arxiv.org/abs/1902.00363v1",
    "https://arxiv.org/abs/1902.00358v1",
    "https://arxiv.org/abs/1902.00287v1",
    "https://arxiv.org/abs/1902.00175v1",
    "https://arxiv.org/abs/1902.00163v1",
    "https://arxiv.org/abs/1902.00137v1",
    "https://arxiv.org/abs/1902.00120v1",
    "https://arxiv.org/abs/1902.00098v1",
    "https://arxiv.org/abs/1902.00089v1",
    "https://arxiv.org/abs/1902.00045v1",
    "https://arxiv.org/abs/1902.00040v1",
    "https://arxiv.org/abs/1902.00016v1",
    "https://arxiv.org/abs/1902.00014v1",
    "https://arxiv.org/abs/1808.03958v3",
    "https://arxiv.org/abs/1806.10115v3",
    "https://arxiv.org/abs/1806.06628v4",
    "https://arxiv.org/abs/1805.10002v4",
    "https://arxiv.org/abs/1902.00304v1",
    "https://arxiv.org/abs/1902.00275v1",
    "https://arxiv.org/abs/1902.00107v1",
    "https://arxiv.org/abs/1902.01128v1",
    "https://arxiv.org/abs/1902.01119v1",
    "https://arxiv.org/abs/1902.01080v1",
    "https://arxiv.org/abs/1902.01073v1",
    "https://arxiv.org/abs/1902.01030v1",
    "https://arxiv.org/abs/1902.00916v1",
    "https://arxiv.org/abs/1902.00908v1",
    "https://arxiv.org/abs/1902.00771v1",
    "https://arxiv.org/abs/1902.00719v1",
    "https://arxiv.org/abs/1902.00685v1",
    "https://arxiv.org/abs/1902.00672v1",
    "https://arxiv.org/abs/1902.00659v1",
    "https://arxiv.org/abs/1902.00655v1",
    "https://arxiv.org/abs/1902.00626v1",
    "https://arxiv.org/abs/1902.00624v1",
    "https://arxiv.org/abs/1902.00604v1",
    "https://arxiv.org/abs/1902.00577v1",
    "https://arxiv.org/abs/1902.00541v1",
]

# URLs = ["https://j.mp/websniffer", "http://j.mp/2Bo2LVf", "http://bit.ly/2BombJQ", "https://cnn.it/2Ggb2ih"]

try:
    shortener = Shortener(tokens=TOKENS)
    urls = random.sample(URLs, k=min(len(URLs), {"none": 0, "one": 1, "some": 3, "all": len(URLs)}["one"]))
    print(shortener.shorten_urls(urls))
    print(shortener.shorten_urls(urls))  # Should use cache.

except Exception:
    time.sleep(0.01)  # Delay for longs to flush.
    raise
