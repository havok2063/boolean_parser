# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: test_clauses.py
# Project: tests
# Author: Brian Cherinka
# Created: Friday, 1st March 2019 3:08:52 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 3rd March 2019 4:28:05 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import pytest
from boolean_parser.clauses import words, condition, between_cond


@pytest.mark.parametrize('value, exp', [('stuff', 'stuff')])
def test_words(value, exp):
    res = words.parseString(value).asDict()
    assert repr(res['words']) == exp
    assert res['words'].name == 'stuff'


@pytest.mark.parametrize('value, exp', [('a > 5', 'a>5')])
def test_condition(value, exp):
    res = condition.parseString(value).asDict()
    assert repr(res['condition']) == exp
    assert res['condition'].value == '5'
    assert res['condition'].fullname == 'a'
    assert res['condition'].operator == '>'


@pytest.mark.parametrize('value, exp', [('a between 3 and 5', 'abetween3and5')])
def test_between_condition(value, exp):
    res = between_cond.parseString(value).asList()
    assert repr(res[0]) == exp
    assert res[0].value == '3'
    assert res[0].value2 == '5'
    assert res[0].fullname == 'a'
    assert res[0].operator == 'between'
