# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: test_sqla.py
# Project: parsers
# Author: Brian Cherinka
# Created: Sunday, 3rd March 2019 4:40:36 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 3rd March 2019 4:43:41 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import pytest
from boolean_parser.parsers import SQLAParser
from tests.models import ModelA, ModelB
from sqlalchemy.sql.expression import BinaryExpression, BooleanClauseList
from sqlalchemy.orm import aliased


def _make_filter(value):
    ModelA2 = aliased(ModelA, name="modela2")
    e = SQLAParser(value).parse()
    f = e.filter([ModelA, ModelB, ModelA2])
    return f

@pytest.mark.parametrize(
    "val, exp",
    [
        ("modela.x > 5", "modela.x > 5"),
        ("modela.x < 5", "modela.x < 5"),
        ("modela.x = 5", "modela.x = 5"),
        ("modela.x == 5", "modela.x = 5"),
        ("modela.name = Some_string", "lower(lower(modela.name)) LIKE lower('%' || 'Some_string' || '%')",),
        ('modela.name == "Some_string"', "lower(modela.name) = lower('Some_string')"),
        ("modela.name = null", "modela.name IS NULL"),
        ("modela.name == null", "modela.name IS NULL"),
        ("modela.bools = True", "modela.bools = true"),
        ("modela.bools == False", "modela.bools = false"),
        ("modela.dates = 2020-01-01", "modela.dates = lower('2020-01-01 00:00:00')"),
        ("modela.dates == 2020-01-01T00:00:00", "modela.dates = lower('2020-01-01 00:00:00')",),
    ],
    ids=[
        "gt",
        "lt",
        "eq",
        "eqeq",
        "eqstr",
        "eqeqstr",
        "null",
        "eqnull",
        "bool",
        "eqbool",
        "date",
        "eqdate",
    ],
)
def test_parse_filter(val, exp):
    ''' test a sqlalchemy filter parse '''
    f = _make_filter(val)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert exp == ww


@pytest.mark.parametrize('query, kls',
                         [('modela2.x < 3', BinaryExpression),
                          ('modela.x > 5 AND modela2.x < 3', BooleanClauseList)],
                         ids=['single', 'multi'])
def test_parse_filter_with_alias(query, kls):
    ''' test a sqlalchemy filter parse with an aliased class '''
    f = _make_filter(query)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, kls)
    assert query == ww


@pytest.fixture(autouse=True)
def batch(model_a_factory):
    ''' batch create some models '''
    model_a_factory.create_batch(20)


def test_query(session):
    ''' test a standard query '''
    res = session.query(ModelA).filter(ModelA.x > 5).all()
    assert len(res) > 0 and len(res) < 20


@pytest.mark.parametrize(
    "val, exp",
    [
        ("modela.dates > 2020-01-01", 0),
        ("modela.dates < 2020-01-01", 20),
        ("modela.dates < 2020-01-01T00:00:00", 20),
        ("modela.dates < 2020-01-01T00:00", 20),
        ("modela.nulls == NULL", 20),
        ("modela.nulls != Null", 0),
        ('modela.bools = True" ', 20),
        ('modela.bools = t" ', 20),
        ('modela.bools = 1" ', 20),
        ('modela.bools = yes" ', 20),
        ('modela.bools != False" ', 20),
        ('modela.bools != f" ', 20),
        ('modela.bools != 0" ', 20),
        ('modela.bools != no" ', 20),
    ],
    ids=[
        "gtdate",
        "ltdate",
        "ltdateiso_a",
        "ltdateiso_b",
        "eqnull",
        "neqnull",
        "bool",
        "bool_a",
        "bool_b",
        "bool_c",
        "nebool",
        "nebool_a",
        "nebool_b",
        "nebool_c",
    ],
)
def test_query_with_filter(session, val, exp):
    ''' test a query with a parsed filter '''
    f = _make_filter(val)
    res = session.query(ModelA).filter(f).all()
    assert len(res) == exp
