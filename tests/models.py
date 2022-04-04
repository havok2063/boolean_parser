# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: models.py
# Project: tests
# Author: Brian Cherinka
# Created: Friday, 15th February 2019 2:44:13 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 3rd March 2019 4:47:18 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

from sqlalchemy import Column, Date, String, BigInteger, Integer, Float
from .database import Base, engine, Session
import factory
import factory.fuzzy
from pytest_factoryboy import register

import datetime

class ModelA(Base):
    __tablename__ = 'modela'
    pk = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    nulls = Column(Integer, nullable=True)
    dates = Column(Date, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<ModelA(pk={self.pk},name={self.name},x={self.x},y={self.y})>'


class ModelB(Base):
    __tablename__ = 'modelb'
    pk = Column(BigInteger, primary_key=True)
    z = Column(Float, nullable=False)

    def __repr__(self):
        return f'<ModelB(pk={self.pk},z={self.z})>'


@register
class ModelAFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ModelA
        sqlalchemy_session = Session   # the SQLAlchemy session object
    pk = factory.Sequence(lambda n: n)
    x = factory.Faker('pyint', min_value=0, max_value=20)
    y = factory.Faker('pyint', min_value=0, max_value=20)
    name = factory.fuzzy.FuzzyText(prefix='model', length=3)
    nulls = factory.Sequence(lambda n: None)
    dates = factory.Faker(
        'date_between_dates',
        date_start=datetime.date(2000, 1, 1),
        date_end=datetime.date(2020, 1, 1),
    )


@register
class ModelBFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ModelB
        sqlalchemy_session = Session   # the SQLAlchemy session object
    pk = factory.Sequence(lambda n: n)
    z = factory.Faker('pyint', min_value=0, max_value=20)


Base.metadata.create_all(engine)
