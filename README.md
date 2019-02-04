# bitlyshortener
**bitlyshortener** is a Python-based high-volume caching-enabled Bitly V4 URL shortener.
It requires and uses one or more generic access tokens provided by Bitly which it uses semi-randomly.
It is nevertheless limited by per-IP rate limits.
As a disclaimer, this is an unofficial package and it has no association with Bitly.

Expanding a shortened URL and other Bitly operations are outside the scope of this package.

## Usage
To obtain an access token:
* Create and log in to a Bitly account.
* In the account profile, navigate to Generic Access Token.
* Enter password and click Generate Token.

To install the package, using Python 3.7+, run:

    pip install bitlyshortener

Usage examples:
```python
from bitlyshortener import Shortener

tokens_pool = ['9fbe2864bb8872f5027c103321ff91be90aea687', '0cbe3864bc8872f5027c103321ff91be30aea787']
shortener = Shortener(tokens=tokens_pool, max_cache_size=8192)

# Shorten a single long URL
shortener.shorten_url('https://python.org/')
'https://j.mp/2BiXLkS'

# Shorten multiple long URLs
urls = ['https://paperswithcode.com/latest', 'https://towardsdatascience.com/machine-learning/home',
        'https://research.fb.com/publications/']
shortener.shorten_urls(urls)
['https://j.mp/2GhpsxU', 'https://j.mp/2RzN02I', 'https://j.mp/2Gj5TFq']
```

To obtain the fastest response, URLs must not be shortened one at a time using `shorten_url`, but in a batch instead
using `shorten_urls`, as in the second example above.

Returned short links use the `j.mp` domain with HTTPS.
