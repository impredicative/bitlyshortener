# bitly-v4-shortener
**bitly-v4-shortener** is a Python based high-volume caching-enabled [Bitly V4](https://dev.bitly.com/v4_documentation.html) URL shortener. It requires and uses one or more OAuth tokens provided by Bitly which it uses semi-randomly. It will still be limited by per-IP rate limits. As a disclaimer, this is an unofficial package and it has no association with Bitly.

Expanding a shortened URL or performing other Bitly operations are outside the scope of this package.

## Installation
Using Python 3.7+, run:

    pip install bitlyv4shortener

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
