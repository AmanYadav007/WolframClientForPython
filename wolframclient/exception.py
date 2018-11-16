# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from wolframclient.language.exceptions import WolframLanguageException
from wolframclient.logger.utils import str_trim


class RequestException(WolframLanguageException):
    """Error in HTTP request."""

    def __init__(self, response, msg=None):
        self.response = response
        if msg:
            self.msg = msg
        else:
            try:
                self.msg = response.text()
            except UnicodeDecodeErrors:
                self.msg = 'Failed to decode request body.'

    def __str__(self):
        return '<%s>: %s' % (self.response.status(), self.msg or '')


class AuthenticationException(RequestException):
    """Error in authentication request."""


class WolframKernelException(WolframLanguageException):
    """Error while interacting with a Wolfram Kernel."""


class WolframEvaluationException(WolframLanguageException):
    """Error after an evaluation raising messages."""

    def __init__(self, error, result=None, messages=[]):
        self.error = error
        self.result = result
        if isinstance(messages, list):
            self.messages = messages
        else:
            self.messages = [messages]

    def __str__(self):
        return self.error

    def __repr__(self):
        return 'WolframEvaluationException<error=%s, expr=%s, messages=%i>:' % (
            self.error, str_trim(self.result), len(self.messages))


class SocketException(WolframLanguageException):
    """Error while operating on socket."""


class WolframParserException(WolframLanguageException):
    """Error while deserializing WXF bytes."""


__all__ = [
    'WolframLanguageException', 'RequestException', 'AuthenticationException',
    'WolframKernelException', 'SocketException', 'WolframParserException'
]
