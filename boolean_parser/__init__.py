# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: __init__.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 1:15:25 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Thursday, 14th February 2019 3:46:32 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

import six
from pyparsing import ParseException
from boolean_parser.conditions import expr


class BooleanParserException(Exception):
    pass


class Parser(object):
    ''' '''

    def __init__(self, value=None):
        self.params = []
        self.original_input = value

        if self.original_input:
            self.parse()
        
    def parse(self, value=None):
        ''' Parse a string conditional '''

        value = value or self.original_input
        assert value is not None, 'There must be some input to parse'
        assert isinstance(value, six.string_types), 'input must be a string'

        try:
            expression = expr.parseString(value)[0]
        except ParseException as e:
            raise BooleanParserException("Parsing syntax error ({0}) at line:{1}, "
                                         "col:{2}".format(e.markInputline(), e.lineno, e.col))
        else:
            return expression
        
    def __repr__(self):
        return f'<Parser(input="{self.original_input or ""}")>'         


def parse(value):
    ''' '''
    try:
        expression = expr.parseString(value)[0]
    except ParseException as e:
        raise BooleanParserException("Parsing syntax error ({0}) at line:{1}, "
                                     "col:{2}".format(e.markInputline(), e.lineno, e.col))
    else:
        expression.original_input = value
        return expression

