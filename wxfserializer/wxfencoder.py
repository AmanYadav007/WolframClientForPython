# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from wxfserializer.utils import six

import wxfserializer.wxfexpr as wxfexpr

class NotEncodedException(Exception):
    ''' Exception used during encoding to signal that a given python
    object has been ignored by a `WXFEncoder`.
    '''
    pass

class WXFEncoder(object):
    ''' Encode a given python object into a stream of `WXFExpr`.

    This class is meant to be subclassed in order to add support for
    new classes. The encoder does not have to do anything since more
    than one can be attached to a given `WXFExprProvider`. The library
    provides a default encoder that should cover basic needs, more or
    less json types, and that should be useful in any case.

    To implement a new encoder one needs to sub-class `WFXEncoder` and
    implements method `encode`. Encode is a generator function that
    takes a given python object and yield `WXFExpr`. If it returns before
    yielding anything a `NotEncodedException`is raised to signal that
    the encoder is not supporting the given object, and that the encoding
    must be delegating to the next encoder (if any).

    Sometimes it is useful to start a new serialization using the provider,
    re-entrant call, especially when dealing with non-atomic `WXFExpr` such
    as Function or Association. To do so one must call `serialize` on the
    target object and yield the results (yield from in PY3).
    '''
    __slots__ = '_provider'
    def __init__(self):
        self._provider = None

    def encode(self, o):
        ''' The method to implement in sub-classes.'''
        raise NotImplementedError

    def serialize(self, o):
        ''' Re-entrant method used to serialize part of a python object.

        Example: when serializing a custom class `foo[{'k1'->1,'k2'->2}]`, the user
        defined encoder for class foo could encode it as a function
        with head 'foo' and a dict:
        >>> yield WXFFunction(3)
        >>> yield WXFSymbol('foo')
        >>> yield from self.serialize({'k1'->1,'k2'->2})

        Using a re-entrant call (line 3) allows the dictionnary to be encoded as a new expr;
        assuming `WXFDefaultEncoder` is registered in the provider, the dict will
        get encoded as an association.

        It also enables transformation mechanism, say apply list to all iterable object and
        pass the result to the provider.
        '''
        for sub in self._provider.provide_wxfexpr(o):
            yield sub

    def _encode(self, o):
        ''' Called by the provider.'''
        value = None
        for value in self.encode(o):
            yield value
        if value is None:
            raise NotEncodedException

class DefaultWXFEncoder(WXFEncoder):
    '''
    The most straight forward serialization of python expressions to their
    Wolfram Language equivalent.

    This class is meant to represent basically JSON like
    objects, and is intended to be used in all providers. As such it should only deal
    with obvious convertion, e.g: `int` to `Integer`, but iterator are not supported.
    They can be added easily though.
    '''
    def encode(self, pythonExpr):
        if isinstance(pythonExpr, six.string_types):
            yield wxfexpr.WXFExprString(pythonExpr)
        elif isinstance(pythonExpr, six.integer_types):
            yield wxfexpr.WXFExprInteger(pythonExpr)
        elif isinstance(pythonExpr, list):
            yield wxfexpr.WXFExprFunction(len(pythonExpr))
            yield wxfexpr.WXFExprSymbol('List')
            for pyArg in iter(pythonExpr):
                for wxf_expr in self.serialize(pyArg):
                    yield wxf_expr
        elif isinstance(pythonExpr, dict):
            yield wxfexpr.WXFExprAssociation(len(pythonExpr))
            for key, value in pythonExpr.items():
                yield wxfexpr.WXFExprRule()
                for wxf_expr in self.serialize(key):
                    yield wxf_expr
                for wxf_expr in self.serialize(value):
                    yield wxf_expr
        elif pythonExpr is True:
            yield wxfexpr.WXFExprSymbol('True')
        elif pythonExpr is False:
            yield wxfexpr.WXFExprSymbol('False')
        elif pythonExpr is None:
            yield wxfexpr.WXFExprSymbol('None')
        elif isinstance(pythonExpr, float):
            yield wxfexpr.WXFExprReal(pythonExpr)
        elif isinstance(pythonExpr, complex):
            yield wxfexpr.WXFExprFunction(2)
            yield wxfexpr.WXFExprSymbol('Complex')
            yield wxfexpr.WXFExprReal(pythonExpr.real)
            yield wxfexpr.WXFExprReal(pythonExpr.imag)