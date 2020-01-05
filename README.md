# bitlyshortener
**bitlyshortener** is a Python 3.7 based high-volume Bitly V4 URL shortener with a memory-cache.
It requires and uses one or more generic access tokens provided by Bitly which it uses semi-randomly.
It is nevertheless limited by per-IP rate limits.
As a disclaimer, this is an unofficial package and it has no association with Bitly.

Other Bitly operations are outside the scope of this package.

[![cicd badge](https://github.com/impredicative/bitlyshortener/workflows/cicd/badge.svg?branch=master)](https://github.com/impredicative/bitlyshortener/actions?query=workflow%3Acicd+branch%3Amaster)

## Links
* Code: https://github.com/impredicative/bitlyshortener/
* Release: https://pypi.org/project/bitlyshortener/

## Requirements
This package doesn't include any access token. To obtain one:
* Sign up for a new Bitly account.
An email address such as `YourGmailUsername+RandomSuffix@gmail.com` should work.
* Verify the email address by clicking the link in the confirmation email.
It can sometimes be necessary to have the confirmation email resent.
* In the account profile, navigate to Generic Access Token.
* Enter password and click Generate Token.

The following are the known rate limits per token:
* Per minute: 100 (presumably for status 200 or 201) [[ref]](https://dev.bitly.com/v4/#section/Rate-Limiting)
* Per hour: 1000 (presumably for status 200 or 201) [[ref]](https://dev.bitly.com/v4/#section/Rate-Limiting) 
* Per month: 1000 (presumably for status 201 only) [[ref] (requires login)](https://app.bitly.com/organization/1/detail)

Python 3.7+ is required.
Any older version of Python will not work due to the use of 
[`ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)
with an *initializer*.

## Usage
To install the package, run:

    pip install bitlyshortener

Usage examples:
```python
from bitlyshortener import Shortener

tokens_pool = ['9fbe2864bb8872f5027c103321ff91be90aea687', '0cbe3864bc8872f5027c103321ff91be30aea787']  # Use your own.
shortener = Shortener(tokens=tokens_pool, max_cache_size=8192)

# Shorten to list
urls = ['https://paperswithcode.com/sota', 'https://arxiv.org/', 'https://arxiv.org/list/cs.LG/recent']
shortener.shorten_urls(urls)
['https://j.mp/2TuIwfz', 'https://j.mp/2t8R7cu', 'https://j.mp/2GohbIt']

# Shorten to dict
urls = ['https://news.google.com', 'https://yahoo.com/']
shortener.shorten_urls_to_dict(urls)
{'https://news.google.com': 'https://j.mp/2TzvYnq', 'https://yahoo.com/': 'https://j.mp/2TCihE4'}

# Normalize diverse preexisting Bitly links
urls = ['http://j.mp/2Bo2LVf', 'http://bit.ly/2BombJQ', 'https://cnn.it/2Ggb2ih', 'https://j.mp/websniffer']
shortener.shorten_urls(urls)
['https://j.mp/2BtckCt', 'https://j.mp/2BlS1qw', 'https://j.mp/2TEVtUt', 'https://j.mp/2BmjqbZ']

# Show cache info
shortener.cache_info
{'Shortener._long_url_to_int_id': CacheInfo(hits=0, misses=9, maxsize=2048, currsize=9)}
```

To obtain the fastest response, URLs must be shortened together in a batch as in the examples above.
A thread pool of up to 32 concurrent requesters can be used, but no more than up to five per randomized token.
For example, if two tokens are supplied, up to 2 * 5 = 10 concurrent workers are used.
If eight tokens are supplied, then not 8 * 5 = 40, but a max of 32 concurrent workers are used.
The max limit can, if really necessary, be increased by setting `config.MAX_WORKERS` before initializing the shortener.

Returned short links use the `j.mp` domain with HTTPS.
Any preexisting Bitly short links are also normalized to use this domain.
