# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: conftest.py
# Project: tests
# Author: Brian Cherinka
# Created: Thursday, 14th February 2019 6:04:55 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Friday, 15th February 2019 2:42:14 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# this fixture creates the Flask app
@pytest.fixture(scope='session')
def app(database):
    ''' Create a Flask app context for the tests. '''
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config[' SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app


# this fixture creates the database connection
@pytest.fixture(scope='session')
def database(app, request):
    ''' Create a database for the tests, and drop it when the tests are done. '''
    db = SQLAlchemy(app=app)
    db.create_all()
    yield db
    db.drop_all()


# this fixture is required for pytest-flask-sqlalchemy
@pytest.fixture(scope='session')
def _db(database):
    ''' Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection. '''
    return database
