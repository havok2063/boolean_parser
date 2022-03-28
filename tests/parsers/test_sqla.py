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


def test_parse_filter_gt_int():
    ''' test a sqlalchemy filter parse '''
    d = 'modela.x > 5'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert d == ww


def test_parse_filter_lt_int():
    ''' test a sqlalchemy filter parse '''
    d = 'modela.x < 5'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert d == ww


def test_parse_filter_eq_int():
    ''' test a sqlalchemy filter parse '''
    d = 'modela.x = 5'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert d == ww


def test_parse_filter_straight_eq_int():
    ''' test a sqlalchemy filter parse '''
    d_straight_eq = 'modela.x == 5'
    f_straight_eq = _make_filter(d_straight_eq)
    ww_straight_equals = str(f_straight_eq.compile(compile_kwargs={'literal_binds': True}))

    d_eq = 'modela.x = 5'
    f_eq = _make_filter(d_eq)
    ww_equals = str(f_eq.compile(compile_kwargs={'literal_binds': True}))

    assert f_eq is not None
    assert f_straight_eq is not None
    assert isinstance(f_eq, BinaryExpression)
    assert isinstance(f_straight_eq, BinaryExpression)

    # in the case of int, they should evaluate to the same expression
    assert ww_equals == ww_straight_equals


def test_parse_filter_eq_str():
    ''' test a sqlalchemy filter parse '''
    d = 'modela.name = Some_string'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert ww == "lower(lower(modela.name)) LIKE lower('%' || 'Some_string' || '%')"


def test_parse_filter_straight_eq_str():
    ''' test a sqlalchemy filter parse '''
    d_straight_eq = 'modela.name == "Some_string"'
    f_straight_eq = _make_filter(d_straight_eq)
    ww_straight_equals = str(f_straight_eq.compile(
        compile_kwargs={'literal_binds': True}))

    d_eq = 'modela.name = "Some_string"'
    f_eq = _make_filter(d_eq)
    ww_equals = str(f_eq.compile(
        compile_kwargs={'literal_binds': True}))

    assert f_eq is not None
    assert f_straight_eq is not None
    assert isinstance(f_eq, BinaryExpression)
    assert isinstance(f_straight_eq, BinaryExpression)

    # in the case of str, they should evaluate to something different
    assert ww_equals == "lower(lower(modela.name)) LIKE lower('%' || 'Some_string' || '%')"
    assert ww_straight_equals == "lower(modela.name) = lower('Some_string')"


def test_parse_filter_eq_null():
    ''' test a sqlalchemy filter parse '''
    d = 'modela.name = null'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert ww == "modela.name IS NULL"


def test_parse_filter_straight_eq_null():
    ''' test a sqlalchemy filter parse '''
    d_straight_eq = 'modela.name == null'
    f_straight_eq = _make_filter(d_straight_eq)
    ww_straight_equals = str(f_straight_eq.compile(
        compile_kwargs={'literal_binds': True}))

    d_eq = 'modela.name = null'
    f_eq = _make_filter(d_eq)
    ww_equals = str(f_eq.compile(
        compile_kwargs={'literal_binds': True}))

    assert f_eq is not None
    assert f_straight_eq is not None
    assert isinstance(f_eq, BinaryExpression)
    assert isinstance(f_straight_eq, BinaryExpression)

    # in the case of str, they should evaluate to something different
    assert ww_equals == "modela.name IS NULL"
    assert ww_equals == ww_straight_equals


def test_parse_filter_eq_date():
    ''' test a sqlalchemy filter parse '''
    d = 'modela.dates = 2020-01-01'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert ww == "lower(modela.dates) = lower('2020-01-01')"


def test_parse_filter_straight_eq_date():
    ''' test a sqlalchemy filter parse '''
    d_straight_eq = 'modela.dates == 2020-01-01'
    f_straight_eq = _make_filter(d_straight_eq)
    ww_straight_equals = str(f_straight_eq.compile(
        compile_kwargs={'literal_binds': True}))

    d_eq = 'modela.dates = 2020-01-01'
    f_eq = _make_filter(d_eq)
    ww_equals = str(f_eq.compile(
        compile_kwargs={'literal_binds': True}))

    assert f_eq is not None
    assert f_straight_eq is not None
    assert isinstance(f_eq, BinaryExpression)
    assert isinstance(f_straight_eq, BinaryExpression)

    # in the case of str, they should evaluate to something different
    assert ww_equals == "lower(modela.dates) = lower('2020-01-01')"
    assert ww_equals == ww_straight_equals


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


def test_query_with_filter_gt_date(session):
    ''' test a query with a parsed filter '''
    d = 'modela.dates > 2020-01-01'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    res = session.query(ModelA).filter(f).all()
    assert len(res) == 0


def test_query_with_filter_lt_date(session):
    ''' test a query with a parsed filter '''
    d = 'modela.dates < 2020-01-01'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    res = session.query(ModelA).filter(f).all()
    assert len(res) == 20


def test_query_with_filter_eq_null(session):
    ''' test a query with a parsed filter '''
    d = 'modela.nulls == NULL'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    res = session.query(ModelA).filter(f).all()
    assert len(res) == 20


def test_query_with_filter_nq_null(session):
    ''' test a query with a parsed filter '''
    d = 'modela.nulls != Null'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    res = session.query(ModelA).filter(f).all()
    assert len(res) == 0
