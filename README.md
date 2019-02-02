# bitly-v4-shortener
**bitly-v4-shortener** is an unofficial Python based high-volume caching-enabled [Bitly V4](https://dev.bitly.com/v4_documentation.html) URL shortener. It requires and uses multiple OAuth tokens which it uses semi-randomly. It will still be limited by per-IP limits.

There is intentionally no support for expanding a shortened URL or for other Bitly operations.

## Installation
Using Python 3.7+:
```pip install bitlyv4shortener```

## Usage
```python
from bitlyv4shortener import Shortener

oauth_tokens_pool = ['9fbe2864bb8872f5027c103321ff91be90aea687', '0cbe3864bc8872f5027c103321ff91be30aea787']
shortener = Shortener(max_cache_size=8192, oauth_tokens=oauth_tokens_pool)
urls = ['https://paperswithcode.com/latest', 'https://towardsdatascience.com/machine-learning/home',
        'https://research.fb.com/publications/']
print(shortener.shorten(urls))
['https://j.mp/2GhpsxU', 'https://j.mp/2RzN02I', 'https://j.mp/2Gj5TFq']
```
