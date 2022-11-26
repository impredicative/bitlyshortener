# bitlyshortener
**bitlyshortener** is a Python 3.7 based high-volume Bitly V4 URL shortener with a memory-cache.
It requires and uses one or more generic access tokens provided by Bitly which it uses semi-randomly.
As a disclaimer, this is an unofficial package and it has no association with Bitly.

**As of 2022, the maintenance of this package has been discontinued because Bitly dramatically lowered their free quota per token to just 50 URLs per month. Users can consider switching to [dagdshort](https://github.com/impredicative/dagdshort) as an alternative.**

Other Bitly operations are outside the scope of this package.

[![cicd badge](https://github.com/impredicative/bitlyshortener/workflows/cicd/badge.svg?branch=master)](https://github.com/impredicative/bitlyshortener/actions?query=workflow%3Acicd+branch%3Amaster)

## Links
| Caption   | Link                                                     |
|-----------|----------------------------------------------------------|
| Repo      | https://github.com/impredicative/bitlyshortener/         |
| Changelog | https://github.com/impredicative/bitlyshortener/releases |
| Package   | https://pypi.org/project/bitlyshortener/                 |

## Requirements
### Tokens
#### Obtaining tokens
This package doesn't include any access token. To obtain one:
* Sign up for a new Bitly account at [https://bitly.com/a/sign_up](https://nullrefer.com/?https://bitly.com/a/sign_up).
An email address such as `YourGmailUsername+SomeSuffix01@gmail.com` should work.
* On the "Let's keep this short" page, click "Skip to your homepage".
* Verify the email address by clicking the link in the confirmation email.
This is a necessary step.
It can on rare occasions be necessary to have the confirmation email resent.
* Under "Profile Settings", select "Generic Access Token".
* Enter password and click Generate Token.

#### Rate limits
In Nov 2022, Bitly sent an email advising that the rate limit per token was lowered to 50 per month, effective Dec 8, 2022.

The following were previously the rate limits per token:
* Per minute: 100 (presumably for status 200 or 201)
* Per hour: 1000 (presumably for status 200 or 201)
* Per month: 1000 (presumably for status 201 only)

Bitly sends a monthly email if 50% of the account's usage limit for new short links is exceeded for the calendar month.
If this email is received, it is suggested to immediately obtain and add additional tokens to the pool used by this package.
As follows, it is preferable to stay under 50% of the usage limit by having a sufficiently big pool of tokens.
It is possible to monitor the usage via the **`.usage()`** method as shown in the examples.

It is unknown what the per-IP rate limit is, if any.

### Python
Python ≥3.7 is required.
Any older version of Python will not work due to the use of 
[`ThreadPoolExecutor`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor)
with an *initializer*.

## Usage
To install the package, run:

    $ pip install bitlyshortener

Usage examples:
```python
>>> import bitlyshortener

# Setup
>>> tokens_pool = ['9fbe2864bb8872f5027c103321ff91be90aea687', '0cbe3864bc8872f5027c103321ff91be30aea787']  # Use your own.
>>> shortener = bitlyshortener.Shortener(tokens=tokens_pool, max_cache_size=256)

# Shorten to list
>>> long_urls = ['https://www.amazon.com/gp/product/B07LFJMS2S/', 'https://www.cnn.com/election/2020', 'https://paperswithcode.com/sota']
>>> shortener.shorten_urls(long_urls)
['https://amzn.to/3Inxf9V', 'https://cnn.it/3FKKZd8', 'https://bit.ly/3tLlp5w']

# Shorten to dict
>>> long_urls = ['https://news.google.com', 'https://yahoo.com/']
>>> shortener.shorten_urls_to_dict(long_urls)
{'https://news.google.com': 'https://bit.ly/3IjSObD', 'https://yahoo.com/': 'https://yhoo.it/2BiHgp8'}

# Normalize diverse preexisting Bitly links
>>> urls = ['http://bit.ly/3Ad49Hw', 'http://j.mp/2Bo2LVf', 'https://cnn.it/3FKKZd8', 'https://j.mp/websniffer']
>>> shortener.shorten_urls(urls)
['https://bit.ly/3Ad49Hw', 'https://bit.ly/3KjocZw', 'https://cnn.it/3FKKZd8', 'https://bit.ly/3nINKph']

# Show usage for tokens pool (is cached for an hour)
>>> shortener.usage()
0.4604  # Means that an average of 46% of the current calendar month's URL shortening quota has been used across all tokens.

# Show cache info
>>> shortener.cache_info
{'Shortener._shorten_url': CacheInfo(hits=4, misses=10, maxsize=256, currsize=10)}
```

To obtain the fastest response, URLs must be shortened together in a batch as in the examples above.
A thread pool of up to 32 concurrent requesters can be used, but no more than up to five per randomized token.
For example, if two tokens are supplied, up to 2 * 5 = 10 concurrent workers are used.
If eight tokens are supplied, then not 8 * 5 = 40, but a max of 32 concurrent workers are used.
The max limit can, if really necessary, be increased by setting `config.MAX_WORKERS` before initializing the shortener.
