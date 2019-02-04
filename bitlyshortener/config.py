API_URL_BITLINKS = 'https://api-ssl.bitly.com/v4/bitlinks'  # Ref: https://dev.bitly.com/v4/#operation/createFullBitlink
API_URL_SHORTEN = 'https://api-ssl.bitly.com/v4/shorten'  # Ref: https://dev.bitly.com/v4/#operation/createBitlink
MAX_CONCURRENT_REQUESTS = 5  # Ref: https://dev.bitly.com/v4/#section/Rate-Limiting
RATE_LIMIT_PER_MINUTE = 100  # Ref: https://dev.bitly.com/v4/#section/Rate-Limiting
RATE_LIMIT_PER_HOUR = 1000  # Ref: https://dev.bitly.com/v4/#section/Rate-Limiting
RATE_LIMIT_PER_MONTH = 10000  # Ref: https://app.bitly.com/organization/1/detail (requires login)
REQUEST_TIMEOUT = 3