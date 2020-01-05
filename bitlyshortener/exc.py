"""Exceptions."""

import logging

log = logging.getLogger(__name__)


class ShortenerError(Exception):
    """Base exception class in this module.

    This exception is not raised directly. All other exception classes in this module hierarchically derive from it.

    :param msg: exception error message.
    """

    def __init__(self, msg: str):
        log.error(msg)
        super().__init__(msg)


class ArgsError(ShortenerError):
    """Exception for shortener initialization argument errors."""


class RequestError(ShortenerError):
    """Exception for upstream request errors."""
