# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: base.py
# Project: parsers
# Author: Brian Cherinka
# Created: Sunday, 17th February 2019 3:43:08 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Friday, 1st March 2019 2:18:11 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import six
import pyparsing as pp
from pyparsing import ParseException
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.clauses import condition, between_cond, words
from boolean_parser.actions.clause import Condition, Word


class BooleanParserException(Exception):
    pass


class Parser(object):
    ''' Standard parser class '''
    _bools = [BoolNot, BoolAnd, BoolOr]

    def __init__(self, value=None):
        self.original_input = value
        self._expression = None

        if self.original_input:
            self._expression = self.parse()

    @property
    def params(self):
        return self._expression.params if self._expression else None

    @property
    def conditions(self):
        return self._expression.conditions if self._expression else None

    def parse(self, value=None):
        ''' Parse a string conditional '''

        value = value or self.original_input
        assert value is not None, 'There must be some input to parse'
        assert isinstance(value, six.string_types), 'input must be a string'

        try:
            expression = self._parser.parseString(value)[0]
        except ParseException as e:
            raise BooleanParserException("Parsing syntax error ({0}) at line:{1}, "
                                         "col:{2}".format(e.markInputline(), e.lineno, e.col))
        else:
            self._expression = expression
            self.original_input = value
            return expression

    def __repr__(self):
        return f'<Parser(input="{self.original_input or ""}")>'

    @classmethod
    def build_parser(cls, clauses=None, bools=None):
        ''' Builds a new boolean parser '''

        where_exp = pp.Forward()
        where_exp <<= clauses

        # extract the Boolean precendent clauses
        bools = bools or cls._bools
        assert len(
            bools) == 3, 'there must be a set of "not, and, or" boolean precedent classes'
        bnot, band, bor = bools

        # build the expression parser
        cls._parser = pp.operatorPrecedence(where_exp, [
            (pp.CaselessLiteral("not"), 1, pp.opAssoc.RIGHT, bnot),
            (pp.CaselessLiteral("and"), 2, pp.opAssoc.LEFT, band),
            (pp.CaselessLiteral("or"), 2, pp.opAssoc.LEFT, bor),
        ])


# Set parse actions
words.setParseAction(Word)
condition.setParseAction(Condition)
between_cond.setParseAction(Condition)

# Build base Parser
clauses = condition | between_cond | words
Parser.build_parser(clauses=clauses)
