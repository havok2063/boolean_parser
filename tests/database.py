# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: database.py
# Project: tests
# Author: Brian Cherinka
# Created: Sunday, 3rd March 2019 4:44:19 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 3rd March 2019 4:49:52 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import pytest
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base


# global database setup
engine = create_engine('sqlite:///:memory:')
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base(bind=engine)


@pytest.fixture(scope='function', autouse=True)
def session():
    session = Session()
    yield session
    session.rollback()
    session.close()

