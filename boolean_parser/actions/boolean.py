# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: boolean.py
# Project: actions
# Author: Brian Cherinka
# Created: Sunday, 17th February 2019 12:52:38 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 12:52:53 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

#
# Boolean Precedent Actions
#


class BaseBool(object):
    ''' Base class for handling conditions joined by boolean logic operators

    This class handles the parsing of boolean logic within strings. The boolean
    classes are assigned to the :py:func:`pyparsing.infixNotation` in the order of boolean
    NOTS->ANDS->ORS, i.e. ``BoolNot``-> ``BoolAnd``-> ``BoolOr``.  For example,
    the string "x > 1 and y < 2", consisting of two conditions joined by a boolean "and" gets
    parsed into "and_(x>1, y<2)", represented as "BoolAnd(Condition1, Condition2)".
    During parsing, the class extracts all conditions and parameters joined by the boolean logic
    and makes them accessible as attributes.

    Attributes:
        params: list
            A list of extracted parameters from all conditions
        conditions: list
            A list of conditions contained within the boolean clause
        logicop: str
            The boolean logic operator used to join the conditions
    '''
    logicop = None

    def __init__(self, data):
        self._get_conditions(data[0])

    def _get_conditions(self, data):
        ''' Builds the list of conditions

        Iterators over the input parsed conditions and extracts
        pyparsed clauses from boolean logic joins. Extracts pyparsed
        conditions into the ``conditions`` parameter.

        Parameters:
            data: list
                A list of underlying conditions
        '''
        self.conditions = []
        for condition in data:
            # append to list if condition is not a Bool class
            if condition and condition != self.logicop:
                self.conditions.append(condition)

    @property
    def params(self):
        ''' The extracted parameters from a parsed condition '''
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
    ''' Class for boolean Not logic '''
    logicop = 'not'


class BoolAnd(BaseBool):
    ''' Class for boolean And logic '''
    logicop = 'and'


class BoolOr(BaseBool):
    ''' Class for boolean Or logic '''
    logicop = 'or'
