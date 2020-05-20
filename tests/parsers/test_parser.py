# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: test_parser.py
# Project: parsers
# Author: Brian Cherinka
# Created: Tuesday, 19th May 2020 10:29:45 am
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2020 Brian Cherinka
# Last Modified: Tuesday, 19th May 2020 10:29:45 am
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

import pytest
from boolean_parser.parsers import Parser
from boolean_parser.actions.clause import Condition


@pytest.mark.parametrize('value, exp', [('stuff', 'stuff')])
def test_words(value, exp):
    res = Parser(value).parse()
    assert repr(res) == exp
    assert res.name == 'stuff'


@pytest.mark.parametrize('value, exp', [('a > 5', 'a>5')])
def test_condition(value, exp):
    res = Parser(value).parse()
    assert repr(res) == exp
    assert res.value == '5'
    assert res.fullname == 'a'
    assert res.operator == '>'
    assert isinstance(res, Condition)


@pytest.mark.parametrize('value, exp', [('a between 3 and 5', 'abetween3and5')])
def test_between_condition(value, exp):
    res = Parser(value).parse()
    assert repr(res) == exp
    assert res.value == '3'
    assert res.value2 == '5'
    assert res.fullname == 'a'
    assert res.operator == 'between'
    assert isinstance(res, Condition)


@pytest.mark.parametrize('value, params',
                         [('a > 5', ['a']),
                          ('a > 5 and b < 3', ['a', 'b'])])
def test_parser_params(value, params):
    pp = Parser(value)
    assert set(params) == set(pp.params)


@pytest.mark.parametrize('value, conditions',
                         [('a > 5', 'a>5'),
                          ('a > 5 and b < 3', ['a>5', 'b<3'])])
def test_parser_conditions(value, conditions):
    pp = Parser(value)
    if not isinstance(conditions, list):
        assert repr(pp.conditions) == conditions
        assert isinstance(pp.conditions, Condition)
    else:
        assert isinstance(pp.conditions, list)
        reps = [repr(c) for c in pp.conditions]
        assert reps == conditions
        assert isinstance(pp.conditions[0], Condition)
