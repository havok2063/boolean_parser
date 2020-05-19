# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: sqla.py
# Project: parsers
# Author: Brian Cherinka
# Created: Sunday, 17th February 2019 12:40:39 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 2:04:29 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
from boolean_parser.parsers import Parser
from boolean_parser.mixins import SQLAMixin
from boolean_parser.actions.clause import Condition
from boolean_parser.actions.boolean import BaseBool, BoolNot, BoolAnd, BoolOr
from boolean_parser.clauses import condition, between_cond
from sqlalchemy.sql import or_, and_, not_


sqlaop = {'and': and_, 'not': not_, 'or': or_}


class SQLACondition(SQLAMixin, Condition):
    ''' '''
    pass


class SQLBoolBase(BaseBool):

    def filter(self, models):
        conditions = [condition.filter(models)
                      for condition in self.conditions]
        return sqlaop[self.logicop](*conditions)


class SQLANot(BoolNot, SQLBoolBase):
    ''' SQLalchemy class for Boolean Not '''


class SQLAAnd(BoolAnd, SQLBoolBase):
    ''' SQLalchemy class for Boolean And '''


class SQLAOr(BoolOr, SQLBoolBase):
    ''' SQLalchemy class for Boolean Or '''


class SQLAParser(Parser):
    _bools = [SQLANot, SQLAAnd, SQLAOr]


# Set new SQLAlchemy parse actions on conditions and build the Parser
clauses = [condition, between_cond]
actions = [SQLACondition, SQLACondition]
SQLAParser.build_parser(clauses=clauses, actions=actions)
