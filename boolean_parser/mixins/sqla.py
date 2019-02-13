# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: sqla.py
# Project: mixins
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 3:49:07 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Wednesday, 13th February 2019 3:49:25 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
from sqlalchemy import func, bindparam, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import or_, and_, not_, sqltypes, between
from operator import le, ge, gt, lt, eq, ne
from boolean_parser.conditions import Condition

opdict = {'<=': le, '>=': ge, '>': gt, '<': lt, '!=': ne, '==': eq, '=': eq}


class SQLAMixin(object):
    ''' '''


class SQLACondition(SQLAMixin, Condition):
    ''' '''
    pass
