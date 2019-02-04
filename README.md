# bitlyshortener
**bitlyshortener** is a Python-based high-volume caching-enabled Bitly V4 URL shortener.
It requires and uses one or more OAuth tokens provided by Bitly which it uses semi-randomly.
It is nevertheless limited by per-IP rate limits.
As a disclaimer, this is an unofficial package and it has no association with Bitly.

Expanding a shortened URL or performing other Bitly operations are outside the scope of this package.

## Installation
Using Python 3.7+, run:

    pip install bitlyshortener

## Usage
To obtain an access token:
* Create and log in to a Bitly account.
* In the account profile, navigate to Generic Access Token.
* Enter password and click Generate Token.

```python
from bitlyshortener import Shortener

tokens_pool = ['9fbe2864bb8872f5027c103321ff91be90aea687', '0cbe3864bc8872f5027c103321ff91be30aea787']
shortener = Shortener(max_cache_len=8192, tokens=tokens_pool)
urls = ['https://paperswithcode.com/latest', 'https://towardsdatascience.com/machine-learning/home',
        'https://research.fb.com/publications/']
print(shortener.shorten(urls))
['https://j.mp/2GhpsxU', 'https://j.mp/2RzN02I', 'https://j.mp/2Gj5TFq']
```

To obtain the fastest response, URLs must not be shortened one at a time, but in a batch instead, as in the above
example.

Returned short links use the `j.mp` domain.
