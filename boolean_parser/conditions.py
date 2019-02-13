# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: conditions.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 1:27:16 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Wednesday, 13th February 2019 3:43:20 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import pyparsing as pp


class BooleanClause(object):
    ''' Base object representing a boolean clause '''
    def __init__(self, data):
        self.data = data[0].asDict()


class Word(BooleanClause):
    ''' Class to handle word clauses '''
    def __init__(self, data):
        super(Word, self).__init__(data)
        self.word = self.data.get('word', None)

    def __repr__(self):
        return f'{self.word}'


class Condition(BooleanClause):
    ''' Class to handle logical expression clauses '''
    def __init__(self, data):
        super(Condition, self).__init__(data)    
        self.name = self.data.get('parameter', None)
        self.operator = self.data.get('operator', None)
        self._extract_values()

    def __repr__(self):
        more = 'and' + self.value2 if hasattr(self, 'value2') else ''
        return self.name + self.operator + self.value + more

    def _extract_values(self):
        ''' Extract the value or values from the condition '''
        self.value = self.data.get('value', None)
        if not self.value:
            if self.operator == 'between':
                self.value = self.data.get('value1')
                self.value2 = self.data.get('value2')


class BoolNot(object):
    ''' Base class for Boolean Not logic '''
    def __init__(self, data):
        self.condition = data[0][1]

    def __repr__(self):
        return f'not_({repr(self.condition)})'


class BoolAnd(object):
    ''' Base class for Boolean And logic '''
    def __init__(self, data):
        self.conditions = []
        for condition in data[0]:
            if condition != 'and':
                self.conditions.append(condition)

    def __repr__(self):
        strcond = ', '.join([repr(c) for c in self.conditions])
        return f'and_({strcond})'


class BoolOr(object):
    ''' Base class for Boolean Or logic '''
    def __init__(self, data):
        self.conditions = []
        for condition in data[0]:
            if condition != 'or':
                self.conditions.append(condition)

    def __repr__(self):
        strcond = ', '.join([repr(c) for c in self.conditions])
        return f'or_({strcond})'


# ------
# define base parser for words
word = pp.Word(pp.alphas).setResultsName('word')
words = pp.Group(word).setResultsName('words')
words.setParseAction(Word)

# ------
# define base parser for logical expressions
number = pp.Regex(r"[+-~]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
name = pp.Word(pp.alphas + '._', pp.alphanums + '._').setResultsName('parameter')
operator = pp.oneOf(['==', '<=', '<', '>', '>=', '=', '!=', '&', '|']).setResultsName('operator')
value = (pp.Word(pp.alphanums + '-_.*') | pp.QuotedString('"') | number).setResultsName('value')
condition = pp.Group(name + operator + value).setResultsName('condition')
condition.setParseAction(Condition)

# ------
# define base parser for between expression
between_cond = pp.Group(name + pp.CaselessLiteral('between').setResultsName('operator') +
                        value.setResultsName('value1') + pp.CaselessLiteral('and') +
                        value.setResultsName('value2'))
between_cond.setParseAction(Condition)

# ------
# define base parser for functions
LPAR = pp.Suppress('(')
RPAR = pp.Suppress(')')
# list of numbers
nl = pp.delimitedList(number, combine=True)
narr = pp.Combine('[' + nl + ']')
# function arguments
arglist = pp.delimitedList(
    number | (pp.Word(pp.alphanums + '-_') + pp.NotAny('=')) | narr)
args = pp.Group(arglist).setResultsName('args')
# function keyword arguments
key = pp.Word(pp.alphas) + pp.Suppress('=')
values = (number | pp.Word(pp.alphas))
keyval = pp.dictOf(key, values)
kwarglist = pp.delimitedList(keyval)
kwargs = pp.Group(kwarglist).setResultsName('kwargs')
# build generic function
fxn_args = pp.Optional(args) + pp.Optional(kwargs)
fxn_name = (pp.Word(pp.alphas)).setResultsName('fxn')
fxn = pp.Group(fxn_name + LPAR + fxn_args + RPAR)
# fxn condition


# ------
# define the recursive where expression
where_exp = pp.Forward()
where_exp <<= condition | between_cond | words

# define the boolean logic precedence order
expr = pp.operatorPrecedence(where_exp, [
    (pp.CaselessLiteral("not"), 1, pp.opAssoc.RIGHT, BoolNot),
    (pp.CaselessLiteral("and"), 2, pp.opAssoc.LEFT, BoolAnd),
    (pp.CaselessLiteral("or"), 2, pp.opAssoc.LEFT, BoolOr),
])

