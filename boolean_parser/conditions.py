# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: conditions.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 1:27:16 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 12:54:38 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import pyparsing as pp

#
# Parsing Action classses
#


class BooleanClause(object):
    ''' Base object representing a boolean clause '''
    def __init__(self, data):
        self.data = data[0].asDict()

        # parse the basic parameter name
        self._parse_parameter_name()
        
    def _parse_parameter_name(self):
        ''' parse the parameter name into a base + name '''
        name = self.data.get('parameter', None)
        assert name.count('.') <= 1, f'parameter {name} cannot have more than one . '
        if '.' in name:
            self.base, self.name = name.split('.', 1)
        else:
            self.base = None
            self.name = name

    @property
    def fullname(self):
        return f'{self.base}.{self.name}' if self.base else self.name


class Word(BooleanClause):
    ''' Class to handle word clauses

    example: alpha and beta or not charlie

    '''
    def __init__(self, data):
        super(Word, self).__init__(data)

    def __repr__(self):
        return f'{self.name}'


class Condition(BooleanClause):
    ''' Class to handle logical expression clauses

    example: x > 5 and y < 3

    '''
    def __init__(self, data):
        super(Condition, self).__init__(data) 

        # extract the conditional operator and value
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
                self.value = self._check_bitwise_value(self.data.get('value1'))
                self.value2 = self._check_bitwise_value(self.data.get('value2'))

        self.value = self._check_bitwise_value(self.value)

    def _check_bitwise_value(self, value):
        ''' check if value has a bitwise ~ in it

        Removes any bitwise ~ found in a value for a condition.
        If the operand is a bitwise & or |, convert the ~value to its
        integer appropriate.  E.g. ~64 -> -65.

        Parameters:
            value (str): A string numerical value

        Returns:
            The str value or value converted to the proper bitwise negative
        '''

        if '~' in value:
            value = value.replace('~', '')
            if self.operator in ['&', '|']:
                value = str(-1 * (int(value)) - 1)

        return value

#
# Boolean Precendent Actions
#


class BaseBool(object):
    logicop = None

    def __init__(self, data):
        self._get_conditions(data[0])

    def _get_conditions(self, data):
        ''' build the list of conditions '''
        self.conditions = []
        for condition in data:
            if condition and condition != self.logicop:
                self.conditions.append(condition)

    @property
    def params(self):
        params = []
        for condition in self.conditions:
            if isinstance(condition, BaseBool):
                params.extend(condition.params)
            else:
                params.append(condition.fullname)
        return list(set(params))

    def __repr__(self):
        strcond = ', '.join([repr(c) for c in self.conditions])
        return f'{self.logicop}_({strcond})'


class BoolNot(BaseBool):
    ''' Base class for Boolean Not logic '''
    logicop = 'not'


class BoolAnd(BaseBool):
    ''' Base class for Boolean And logic '''
    logicop = 'and'


class BoolOr(BaseBool):
    ''' Base class for Boolean Or logic '''
    logicop = 'or'


# ------
# define base parser for words
word = pp.Word(pp.alphas).setResultsName('parameter')
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
# define the recursive where expression
where_exp = pp.Forward()
where_exp <<= condition | between_cond | words

# define the boolean logic precedence order
expr = pp.operatorPrecedence(where_exp, [
    (pp.CaselessLiteral("not"), 1, pp.opAssoc.RIGHT, BoolNot),
    (pp.CaselessLiteral("and"), 2, pp.opAssoc.LEFT, BoolAnd),
    (pp.CaselessLiteral("or"), 2, pp.opAssoc.LEFT, BoolOr),
])

