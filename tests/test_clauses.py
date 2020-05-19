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
from boolean_parser.clauses import words, condition, between_cond, fxn, fxn_cond, fxn_expr

expdata = {'fxn1': {'name': 'test',
                    'args': ['1', '2', '3', 'hello'],
                    'kwargs': {'a': '5', 'stuff': 'there', 'force_check': 'True'}},
           'fxn2': {'name': 'test',
                    'args': ['1', '2', '3', 'hello'],
                    'kwargs': ''},
           'fxn3': {'name': 'test',
                    'args': '',
                    'kwargs': {'a': '5', 'stuff': 'there', 'force_check': 'True'}},
           'fxn4': {'name': 'test',
                    'args': '',
                    'kwargs': ''},
           'fxn_cond': {'function': {'name': 'test',
                                     'args': ['1', '2', '3'],
                                     'kwargs': {'a': '3', 'b': '4'}},
                        'operator': '>',
                        'value': '5'},
           'fxn_expr': {'function_call': {'name': 'test',
                                          'condition': {'parameter': 'x', 'operator': '>', 'value': '1'}},
                        'operator': '<=',
                        'value': '30'},
           'words': {'parameter': 'stuff'},
           'condition': {'parameter': 'a', 'operator': '>', 'value': '5'},
           'between_condition': {'parameter': 'a', 'operator': 'between', 'value1': '3', 'value2': '5'}
           }


@pytest.mark.parametrize('value, exp', [('stuff', expdata['words'])])
def test_words(value, exp):
    ''' test parsing of word clause '''
    res = words.parseString(value).asDict()
    assert 'words' in res
    assert res['words']['parameter'] == exp['parameter']


@pytest.mark.parametrize('value, exp', [('a > 5', expdata['condition'])])
def test_condition(value, exp):
    ''' test parsing of condition clause '''
    res = condition.parseString(value).asDict()
    assert 'condition' in res
    rc = res['condition']
    assert rc['value'] == exp['value']
    assert rc['parameter'] == exp['parameter']
    assert rc['operator'] == exp['operator']


def test_condition_has_default_action():
    ''' test that blank clauses have default actions '''
    assert condition.parseAction == []
    res = condition.parseString('x > 1').asDict()
    assert isinstance(res['condition'], dict)


@pytest.mark.parametrize('value, exp', [('a between 3 and 5', expdata['between_condition'])])
def test_between_condition(value, exp):
    res = between_cond.parseString(value).asDict()
    assert 'between_condition' in res
    bc = res['between_condition']
    assert bc['value1'] == exp['value1']
    assert bc['value2'] == exp['value2']
    assert bc['parameter'] == exp['parameter']
    assert bc['operator'] == exp['operator']


@pytest.mark.parametrize('value, exp',
                         [('test(1, 2, 3, hello, a=5, stuff=there, force_check=True)', expdata['fxn1']),
                          ('test(1, 2, 3, hello)', expdata['fxn2']),
                          ('test(a=5, stuff=there, force_check=True)', expdata['fxn3']),
                          ('test()', expdata['fxn4']),
                          ], ids=['all', 'args-only', 'kwargs-only', 'none'])
def test_function(value, exp):
    res = fxn.parseString(value).asDict()
    assert 'function' in res
    assert res['function']['name'] == exp['name']
    assert res['function']['args'] == exp['args']
    assert res['function']['kwargs'] == exp['kwargs']


@pytest.mark.parametrize('value, exp', [('test(1,2,3,a=3,b=4) > 5', expdata['fxn_cond'])])
def test_function_conditional(value, exp):
    res = fxn_cond.parseString(value).asDict()
    assert 'function_condition' in res
    fc = res['function_condition']
    assert fc['value'] == exp['value']
    assert fc['operator'] == exp['operator']
    assert fc['function'] == exp['function']

    assert fc['function']['name'] == exp['function']['name']
    assert fc['function']['args'] == exp['function']['args']
    assert fc['function']['kwargs'] == exp['function']['kwargs']


@pytest.mark.parametrize('value, exp', [('test(x > 1) <= 30', expdata['fxn_expr'])])
def test_function_expression(value, exp):
    res = fxn_expr.parseString(value).asDict()
    assert 'function_expression' in res
    fe = res['function_expression']
    assert fe['value'] == exp['value']
    assert fe['operator'] == exp['operator']
    assert fe['function_call'] == exp['function_call']

    assert fe['function_call']['name'] == exp['function_call']['name']
    assert fe['function_call']['condition'] == exp['function_call']['condition']

    fc = fe['function_call']['condition']
    ec = exp['function_call']['condition']
    assert fc['parameter'] == ec['parameter']
    assert fc['operator'] == ec['operator']
    assert fc['value'] == ec['value']
