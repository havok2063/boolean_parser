# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: __init__.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 1:15:25 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 3:44:25 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

from boolean_parser.parsers import Parser
from boolean_parser.parsers import SQLAParser


__version__ = '0.1.3'


def parse(value, base='sqla'):
    ''' Convenience function to returned a parsed expression

    Returns a parsed string using one of the available Parsers
    in `boolean_parser`.  The ``base`` keyword argument can be used
    to select which ``Parser`` to use.  The availble bases are: "base",
    "sqla".  The default base is "sqla" which uses the :py:class:`boolean_parser.parsers.sqla.SQLAParser`.

    Parameters:
        value: str
            The string expression to evaluate and parse
        base: str:
            The base Parser to use.  Default is sqlalchemy parser.

    Returns:
        A parsed string using a :ref:`api-parsers` object.
    '''
    if base == 'base':
        return Parser(value).parse()
    elif base == 'sqla':
        return SQLAParser(value).parse()
    else:
        return Parser(value).parse()

