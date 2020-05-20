# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: clause.py
# Project: actions
# Author: Brian Cherinka
# Created: Sunday, 17th February 2019 12:52:31 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 12:53:16 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

#
# Parsing Action classses
#


class BaseAction(object):
    ''' Base object representing a clause action

    An action to perform after parsing a string clause.  If set, actions run
    Actions are attached to clauses with the ``setParseAction`` on a given ``pyparsing``
    element.  :py:meth:`pyparsing.ParserElement.setParseAction` accepts a function or class to
    be applied to the ``pyparsing`` element during the parsing process.  Multiple actions can
    be attached by passing a list of functions or classes.  This class extracts the parsed data
    from the ``pyparsing`` element and makes it accessible as a variety of named attributes.

    Attributes:
        name: str
            The name of the extracted parameter
        base: str
            The base name of the extracted parameter, if any.
        fullname: str
            The full name of the extracted parameter as base + name
        data: dict
            The extracted parsed parameters from the pyparse clause
        parsed_clause: :py:class:`pyparsing.ParseResults`
            The original pyparsed results object
        input_clause: str
            The original input clause element
    '''

    def __init__(self, data):
        self.parsed_clause = data
        self.data = data[0].asDict()

        # parse the basic parameter name
        self._parse_parameter_name()

    def _parse_parameter_name(self):
        ''' parse the parameter name into a base + name '''
        name = self.data.get('parameter', None)
        assert name.count(
            '.') <= 1, f'parameter {name} cannot have more than one . '
        if '.' in name:
            self.base, self.name = name.split('.', 1)
        else:
            self.base = None
            self.name = name

    @property
    def fullname(self):
        ''' The full parameter name, including any base '''
        return f'{self.base}.{self.name}' if self.base else self.name


class Word(BaseAction):
    ''' Class action for handling word clauses

    This action performs a basic word parse.  The basic word
    is assigned as the ``name`` attribute.  Example word clauses:
    "alpha" or "alpha and beta or not charlie".

    '''

    def __init__(self, data):
        super(Word, self).__init__(data)

    def __repr__(self):
        return f'{self.name}'

    @property
    def input_clause(self):
        ''' Original input clause as a string '''
        return f'{self.fullname}'


class Condition(BaseAction):
    ''' Class action for handling conditional clauses

    This action performs a basic conditional parse.  The syntax for a
    conditional expressions is defined as "parameter operand value" or
    for "between" conditions, "parameter between value and value2".  The parameter name,
    operand, and parameter value is assigned as the ``name``, ``operator``, and
    ``value`` attribute, respectively.  Example conditional clauses:
    "x > 5" or "x > 5 and y < 3".  When using a "between" condition, e.g.
    "x between 3 and 5", an additional ``value2`` attribute is assigned the second
    parameter value.  For bitwise operands of '&' and '|', the value can also accept a negation
    prefix, e.g. "x & ~256", which evaluates to "x & -257".

    Allowed operands for conditionals are:
        '>', '>=, '<', '<=', '==', '=', '!=', '&', '|'

    In addition to the Base Attributes, the ``Condition`` action provides
    additional attributes containing the parsed condition parameters.

    Attributes:
        operator: str
            The operand used in the condition
        value: str
            The parameter value in the condition
        value2: str
            Optional second value, assigned when a "between" condition is used.

    '''

    def __init__(self, data):
        super(Condition, self).__init__(data)

        # extract the conditional operator and value
        self.operator = self.data.get('operator', None)
        self._extract_values()

    def __repr__(self):
        more = 'and' + self.value2 if hasattr(self, 'value2') else ''
        return self.name + self.operator + self.value + more

    @property
    def input_clause(self):
        ''' Original input clause as a string '''
        if self.operator == 'between':
            return f'{self.fullname} {self.operator} {self.value} and {self.value2}'
        else:
            return f'{self.fullname} {self.operator} {self.value}'

    def _extract_values(self):
        ''' Extract the value or values from the condition '''
        self.value = self.data.get('value', None)
        if not self.value:
            if self.operator == 'between':
                self.value = self._check_bitwise_value(self.data.get('value1'))
                self.value2 = self._check_bitwise_value(
                    self.data.get('value2'))

        self.value = self._check_bitwise_value(self.value)

    def _check_bitwise_value(self, value):
        ''' Check if value has a bitwise ~ in it

        Removes any bitwise ~ found in a value for a condition.
        If the operand is a bitwise & or |, convert the ~value to its
        integer appropriate.  E.g. ~64 -> -65.

        Parameters:
            value: str
                A string numerical value

        Returns:
            The str value or value converted to the proper bitwise negative
        '''

        if '~' in value:
            value = value.replace('~', '')
            if self.operator in ['&', '|']:
                value = str(-1 * (int(value)) - 1)

        return value

