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
    ''' Base object representing a clause action '''

    def __init__(self, data):
        self.original_parse = data
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
        return f'{self.base}.{self.name}' if self.base else self.name


class Word(BaseAction):
    ''' Class to handle word clauses

    example: alpha and beta or not charlie

    '''

    def __init__(self, data):
        super(Word, self).__init__(data)

    def __repr__(self):
        return f'{self.name}'


class Condition(BaseAction):
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
                self.value2 = self._check_bitwise_value(
                    self.data.get('value2'))

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

