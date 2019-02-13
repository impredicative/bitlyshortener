"""Exceptions."""

import logging

log = logging.getLogger(__name__)


class ShortenerError(Exception):
    """This is the base exception class in this module.

    This exception is not raised directly. All other exception classes in this module hierarchically derive from it.

    :param msg: exception error message.
    """
    #
    def __init__(self, msg: str):
        log.error(msg)
        super().__init__(msg)


class ArgsError(ShortenerError):
    pass


class RequestError(ShortenerError):
    pass
