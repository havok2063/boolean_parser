# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: test_parse.py
# Project: tests
# Author: Brian Cherinka
# Created: Friday, 1st March 2019 3:11:43 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Friday, 1st March 2019 3:50:46 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

import pytest
from boolean_parser import parse
from boolean_parser.parsers.base import BooleanParserException

#
# tests for the global basic parse function
#

# parametrization argument values
arg_values = [
    ('x > 5', 'x>5'),
    ('x > 5 and x < 10', 'and_(x>5, x<10)'),
    ('x between 5 and 10', 'xbetween5and10'),
    ('x > 5 or y < 3', 'or_(x>5, y<3)'),
    ('x > 5 or y < 3 and not z == 2', 'or_(x>5, and_(y<3, not_(z==2)))')
]


@pytest.mark.parametrize('value, exp',
                         [('stuff', 'stuff'),
                          ('stuff and things', 'and_(stuff, things)')] + arg_values)
def test_core_parse(value, exp):
    expr = parse(value, base='core')
    assert exp == repr(expr)


@pytest.mark.parametrize('value, exp', arg_values)
def test_sqla_parse(value, exp):
    expr = parse(value)
    assert exp == repr(expr)


@pytest.mark.parametrize('value', [('stuff'), ('stuff and things')])
def test_sqla_fails(value):
    with pytest.raises(BooleanParserException) as cm:
        parse(value)
    assert 'Parsing syntax error' in str(cm.value)
