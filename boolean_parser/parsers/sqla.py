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
    ''' SQLAlchemy Conditional Action

    Subclasses from ``Condition`` and ``SQLAMixin`` to create an
    action that parses a string that represents a SQLAlchemy filter condition
    and allows for conversion from the parsed string result to a SQLAlchemy
    filter object.  For SQLAlchemy conditions, the syntax for a conditon expression
    is "database_table_name.parameter operand value" where "database_table_name.parameter"
    is a dotted syntax for `ModelClass.parameter` which maps to `dbtable_name.column_name`.
    For example, given a base ModelClass "TableModel" with parameter "x", that maps to a database
    table called "table" with column "x", the conditional expression "table.x < 4" parses into
    "{name: 'x', fullname: 'table.x', base: 'table', operator: '<', value: '4'}"

    '''
    pass


class SQLBoolBase(BaseBool):
    ''' Class for handling boolean logic joins for SQLALchemy filter expressions '''

    def filter(self, models):
        ''' Calls the filter method for each condition

        Parameters:
            models: list
                A list of SQLAlchemy ORM models
        '''
        conditions = [condition.filter(models)
                      for condition in self.conditions]
        return sqlaop[self.logicop](*conditions)


class SQLANot(BoolNot, SQLBoolBase):
    ''' SQLalchemy class for boolean Not '''


class SQLAAnd(BoolAnd, SQLBoolBase):
    ''' SQLalchemy class for boolean And '''


class SQLAOr(BoolOr, SQLBoolBase):
    ''' SQLalchemy class for boolean Or '''


class SQLAParser(Parser):
    ''' A SQLAlchemy boolean parser object

    A Parser class that provides a mechanism for converting a
    string conditional into a SQLAlchemy filter condition that can
    be passed into SQLAlchemy queries.  This parser contains a ``filter``
    method which accepts a list of SQLAlchemy Model classes used to identify
    and convert the parsed parameter name into a SQLAlchemy Instrumented Attribute.

    Example:
        >>> from boolean_parser.parsers import SQLAParser
        >>> from database.models import TableModel
        >>> from database import session
        >>>
        >>> # create the parser and parse a sql condition
        >>> res = SQLParser('table.x > 5 and table.y < 2').parse()
        >>> res
        >>> and_(x>5, y<2)
        >>>
        >>> # generate the sqlalchemy filter
        >>> ff = res.filter(TableModel)
        >>> print(ff.compile(compile_kwargs={'literal_binds': True}))
        >>> table.x > 5 AND table.y < 2
        >>>
        >>> # perform the sqlalchemy query
        >>> session.query(TableModel).filter(ff).all()
    '''
    _bools = [SQLANot, SQLAAnd, SQLAOr]


# Set new SQLAlchemy parse actions on conditions and build the Parser
clauses = [condition, between_cond]
actions = [SQLACondition, SQLACondition]
SQLAParser.build_parser(clauses=clauses, actions=actions)
