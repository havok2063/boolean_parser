# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: sqla.py
# Project: mixins
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 3:49:07 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 3:45:21 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import inspect
import decimal
from sqlalchemy import func, bindparam
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import sqltypes, between
from operator import le, ge, gt, lt, eq, ne
from boolean_parser.parsers.base import BooleanParserException


opdict = {'<=': le, '>=': ge, '>': gt, '<': lt, '!=': ne, '==': eq, '=': eq}

class SQLAMixin(object):
    ''' A Mixin class to apply SQLAlchemy filter parsing

    This mixin adds a ``filter`` method to the parsed result which converts
    the parsed string object into an appropriate SQLAlchemy filter condition to be used
    in SQLAlchemy queries.

    '''

    def _check_models(self, classes):
        ''' Check the input modelclass format

        Checks if input classes is a module of modelclasses, a list of modelclasses
        or a single ModelClass and returns a list of ModelClass objects.

        Parameters:
            classes (object):
                A ModelClass module, list of models, or single ModelClass

        Returns:
            A list of ModelClasses
        '''

        # an entire module of classes
        if inspect.ismodule(classes):
            # an entire module of classes
            models = [i[1] for i in inspect.getmembers(
                classes, inspect.isclass) if hasattr(i[1], '__tablename__')]
        elif isinstance(classes, (list, tuple)):
            # a list of ModelClasses
            models = classes
        else:
            # assume a single ModelClass
            models = [classes]

        # check for proper modelclasses
        allmeta = all([isinstance(m, DeclarativeMeta) or isinstance(m, AliasedClass) for m in models])
        assert allmeta is True, 'All input classes must be of type SQLAlchemy ModelClasses'

        return models

    def _get_field(self, modelclass, field_name, base_name=None):
        ''' Return a SQLAlchemy attribute from a field name.

        Checks that a given model contains the named field.

        Parameters:
            modelclass (ModelClass):
                A SQLAlchemy ModelClass
            field_name (str):
                The database field name
            base_name (str):
                The database table name

        Returns:
            An SQLA instrumented attribute object
        '''

        field = None
        # Handle hierarchical field names such as 'parent.name'
        if base_name:
            # Match alias name
            if isinstance(modelclass, AliasedClass) and \
                    base_name == modelclass._aliased_insp.name.lower():
                field = getattr(modelclass, field_name, None)

            # Match table name
            if not field and base_name in modelclass.__tablename__:
                field = getattr(modelclass, field_name, None)
        else:
            # Handle flat field names such as 'name'
            field = getattr(modelclass, field_name, None)

        return field

    def filter(self, modelclass):
        ''' Return the condition as an SQLalchemy query filter condition

        Loops over all models and creates a filter condition for that model
        given the input filter parameters.

        Parameters:
            modelclass (objects):
                A set of ModelClasses to use in the filter condition

        Returns:
            A SQL query filter condition
        '''

        assert modelclass is not None, 'No input found'

        condition = None
        models = self._check_models(modelclass)

        for model in models:
            # get the SQLA instrumented attribute
            field = self._get_field(model, self.name, base_name=self.base)

            # if there is an attribute then break and use that model
            if field and hasattr(field, 'type') and hasattr(field, 'ilike'):
                break

        # raise if no attribute found
        if not field:
            raise BooleanParserException(f'Table {model.__tablename__} does not have field {self.name}')

        # produce the SQLA filter condition
        condition = self._filter_one(model, field=field, condition=condition)

        return condition

    def _filter_one(self, model, field=None, condition=None):
        ''' Create a single SQLAlchemy filter condition '''

        # if no field present return the original condition
        if not field:
            return condition

        # Prepare field and value
        lower_field, lower_value, lower_value_2 = self._bind_and_lower_value(field)

        # Handle postgresql arrays if any
        if isinstance(field.type, postgresql.ARRAY):
            condition = field.any(self.value, operator=opdict[self.operator])
            return condition

        # Handle scalar values

        # Return SQLAlchemy condition based on operator value
        # self.name is parameter name, lower_field is Table.parameterName
        elif self.operator == '<':
            condition = lower_field.__lt__(lower_value)

        elif self.operator == '<=':
            condition = lower_field.__le__(lower_value)

        elif self.operator == '>':
            condition = lower_field.__gt__(lower_value)

        elif self.operator == '>=':
            condition = lower_field.__ge__(lower_value)

        elif self.operator == '!=':
            field = getattr(model, self.name)
            value = self.value
            # Handle NULL values
            if value.lower() == 'null':
                condition = field.isnot(None)
            else:
                condition = lower_field.__ne__(lower_value)

        elif self.operator == '=' or self.operator == '==':
            # Handle string type
            if isinstance(field.type, sqltypes.TEXT) or \
                isinstance(field.type, sqltypes.VARCHAR) or \
                isinstance(field.type, sqltypes.String):
                field = getattr(model, self.name)
                value = self.value
                # Handle NULL values
                if value.lower() == 'null':
                    condition = field.is_(None)
                # if operator is straing equals, check accordingly
                elif self.operator == '==':
                    condition = lower_field.__eq__(lower_value)
                # otherwise, this operator maps to LIKE
                # x=5   ->  x LIKE '%5%' (x contains 5)
                # x=5*  ->  x LIKE '5%'  (x starts with 5)
                # x=*5  ->  x LIKE '%5'  (x ends with 5)
                elif value.find('*') >= 0:
                    value = value.replace('*', '%')
                    condition = lower_field.ilike(bindparam(self.fullname, value))
                else:
                    condition = lower_field.ilike('%' + bindparam(self.fullname, value) + '%')
            # For all other types, assume straight equality
            else:
                field = getattr(model, self.name)
                value = self.value
                # Handle NULL values
                if value.lower() == 'null':
                    condition = field.is_(None)
                else:
                    condition = lower_field.__eq__(lower_value)

        elif self.operator == 'between':
            # between condition
            condition = between(lower_field, lower_value, lower_value_2)

        elif self.operator in ['&', '|']:
            # bitwise operations
            condition = lower_field.op(self.operator)(lower_value) > 0

        return condition


    def _bind_and_lower_value(self, field):
        ''' Bind and lower the value based on field type'''

        lower_value_2 = None

        # get python field type
        ftypes = [float, int, decimal.Decimal]
        fieldtype = field.type.python_type

        # format the values
        value, lower_field = self._format_value(self.value, fieldtype, field)
        if hasattr(self, 'value2'):
            value2, lower_field = self._format_value(self.value2, fieldtype, field)

        # bind the parameter value to the parameter name
        boundvalue = bindparam(self.fullname, value, unique=True)
        lower_value = func.lower(boundvalue) if fieldtype not in ftypes else boundvalue
        if hasattr(self, 'value2'):
            boundvalue2 = bindparam(self.fullname, value2, unique=True)
            lower_value_2 = func.lower(boundvalue2) if fieldtype not in ftypes else boundvalue2

        return lower_field, lower_value, lower_value_2

    def _format_value(self, value, fieldtype, field):
        ''' Formats the value based on the fieldtype

        Formats the value to proper numreical type and lowercases
        the field for string fields.

        Parameters:
            value (str):
                The conditional value to format
            fieldtype (object):
                The python field type
            field (SQLA attribute):
                SQLA instrumented attribute

        Returns:
            The formatted value and lowercase field
        '''

        lower_field = field
        if fieldtype == float or fieldtype == decimal.Decimal:
            out_value = self._cast_value(value, datatype=float)
        elif fieldtype == int:
            out_value = self._cast_value(value, datatype=int)
        else:
            lower_field = func.lower(field)
            out_value = value

        return out_value, lower_field

    def _cast_value(self, value, datatype=float):
        ''' Cast a value to a specific Python type

        Parameters:
            value (int|float):
                A numeric value to cast to a float or integer
            datatype (object):
                The numeric cast function.  Can be either float or int.

        Returns:
            The value explicitly cast to an integer or float
        '''

        assert datatype in [float, int], 'datatype must be either float or int'
        try:
            if value.lower() == 'null':
                out = 'null'
            else:
                out = datatype(value)
        except (ValueError, SyntaxError):
            raise BooleanParserException(f'Field {self.name} expects a {datatype.__name__} value.  Received {value} instead.')
        else:
            return out

