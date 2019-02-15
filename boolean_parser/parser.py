# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: parser.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Friday, 15th February 2019 3:24:54 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Friday, 15th February 2019 4:12:13 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import six
import pyparsing as pp
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
        
    
    @classmethod
    def build_parser(cls, clauses=None):
        ''' Builds a new boolean parser '''
        
        where_exp = pp.Forward()
        where_exp <<= clauses
        
        cls._parser = pp.operatorPrecedence(where_exp, [
            (pp.CaselessLiteral("not"), 1, pp.opAssoc.RIGHT, BoolNot),
            (pp.CaselessLiteral("and"), 2, pp.opAssoc.LEFT, BoolAnd),
            (pp.CaselessLiteral("or"), 2, pp.opAssoc.LEFT, BoolOr),
        ])
