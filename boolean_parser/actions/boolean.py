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
