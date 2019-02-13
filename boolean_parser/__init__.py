# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: __init__.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 1:15:25 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Wednesday, 13th February 2019 3:47:54 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

from pyparsing import ParseException
from boolean_parser.conditions import expr


class BooleanParserException(Exception):
    pass


def parse(value):
    ''' '''
    try:
        expression = expr.parseString(value)[0]
    except ParseException as e:
        raise BooleanParserException("Parsing syntax error ({0}) at line:{1}, "
                                     "col:{2}".format(e.markInputline(), e.lineno, e.col))
    else:
        return expression

