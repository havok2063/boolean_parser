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
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.orm import aliased


def _make_filter(value):
    ModelA2 = aliased(ModelA, name="modela2")
    e = SQLAParser(value).parse()
    f = e.filter([ModelA, ModelB, ModelA2])
    return f


def test_parse_filter():
    ''' test a sqlalchemy filter parse '''
    d = 'modela.x > 5'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert d == ww

def test_parse_filter_with_alias():
    ''' test a sqlalchemy filter parse with an aliased class '''
    d = 'modela2.x > 5'
    f = _make_filter(d)
    ww = str(f.compile(compile_kwargs={'literal_binds': True}))
    assert f is not None
    assert isinstance(f, BinaryExpression)
    assert d == ww


@pytest.fixture(autouse=True)
def batch(model_a_factory):
    ''' batch create some models '''
    model_a_factory.create_batch(20)


def test_query(session):
    ''' test a standard query '''
    res = session.query(ModelA).filter(ModelA.x > 5).all()
    assert len(res) > 0 and len(res) < 20


def test_query_with_filter(session):
    ''' test a query with a parsed filter '''
    d = 'modela.x > 5'
    f = _make_filter(d)
    res = session.query(ModelA).filter(f).all()
    assert len(res) > 0 and len(res) < 20
