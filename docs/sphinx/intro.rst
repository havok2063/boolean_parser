
.. _intro:

Introduction to boolean_parser
==============================

``boolean_parser`` is a Python package for parsing strings that contain conditional expressions combined with
boolean logic operators.  It uses the `pyparsing <https://pyparsing-docs.readthedocs.io/en/latest/>`_ Python package
for all syntax parsing grammar definitions.


Parsing a String Condition
--------------------------

The :py:func:`boolean_parser.parse` function is a convenience function available to start parsing strings right away
using the built-in ``Parser`` classes.
::

    # import the parse function
    >>> from boolean_parser import parse

    # parse a string condition
    >>> res = parse('x > 3')
    >>> res
    x>3

The parsed result is a ``Condition`` object containing extracted information about the condition.   The `data` attribute
contains a dictionary of all relevant information, while the parameter name, operand, and value are available as
attributes on the ``Condition`` class.
::

    >>> # show the extracted data
    >>> res.data
    {'parameter': 'x', 'operator': '>', 'value': '3'}

    >>> print(res.name, res.operator, res.value)
    x > 3

Boolean Joins
-------------

To combine conditional expressions you can join them using `and`, `or` or `not` boolean operands within the string.
When using boolean operands, the parsed result is a nested set of Boolean Condition classes, i.e. ``BoolAnd``,
``BoolOr``, ``BoolNot`` which contain the ``Conditions`` and preserve the order of the condition hiearchy.
::

    >>> example = 'x > 3 and y <= 2 or not z != 5'
    >>> res = parse(example)
    >>> res
    or_(and_(x>3, y<=2), not_(z!=5))

The order of operations here is `OR` which joins and `AND` and a `NOT` condition.  You can use parantheses
to control condition hierarchy.  Without parantheses, precedence reads left to right.
::

    >>> # without parantheses
    >>> parse('x > 3 and y <= 2 or not z != 5')
    or_(and_(x>3, y<=2), not_(z!=5))

    >>> # with parantheses
    >>> parse('x > 3 and (y <= 2 or not z != 5)')
    and_(x>3, or_(y<=2, not_(z!=5)))

Boolean Condition objects contain only three parameters: `params`, `conditions`, and `logicop`.  ``params`` contains
a list of all parameters within itself.  ``conditions`` contains a list of all conditions within itself.  ``logicop``
indicates the current boolean operator.
::

    >>> # parse a boolean expression
    >>> example = 'x > 3 and y <= 2 or not z != 5'
    >>> res = parse(example)
    >>> res
    or_(and_(x>3, y<=2), not_(z!=5))

    >>> # show the logic operator
    >>> res.logicop
    'or'

    >>> # list the parameters within boolean OR
    >>> res.params
    ['y', 'x', 'z']

    >>> # list the conditions within the boolean OR
    >>> res.conditions
    [and_(x>3, y<=2), not_(z!=5)]

You can drill down through the conditions until you get to the underling conditions.
::

    >>> # access the first "boolean and" condition
    >>> booland = res.conditions[0]
    >>> booland
    and_(x>3, y<=2)

    >>> # show the conditions inside the boolean and
    >>> booland.conditions
    [x>3, y<=2]

    >>> # access the first "x > 3" condition and print data
    >>> xcond = booland.conditions[0]
    >>> xcond.data
    {'parameter': 'x', 'operator': '>', 'value': '3'}

Using a Parser
--------------

The :py:func:`boolean_parser.parse` convenience function
by default uses the ``SQLAParser``.


Parsing SQLAlchemy Filters
--------------------------

The :py:class:`boolean_parser.parsers.sqla.SQLAParser` class for SQLAlchemy provides an
additional ``filter`` function that converts a parsed boolean string into a SQLAlchemy filter condition
useable in SQLAlchemy queries.  Otherwise it behaves exactly the same as the core
:py:class:`boolean_parser.parsers.base.Parser`.

Suppose we have a database with a table "table" and columns "x", and "y".  The SQLAlchemy database session is
defined in a `database` module, along with our SQLAlchemy ORM models, including a "TableModel", defined in a
`database.models` module.  We want to parse the string expression "table.x > 5 and table.y < 2" and use it as
a filter in a SLQLAlchemy query.  First we import our database `session`, ORM `TableModel` and the ``parse`` function,
and parse the string expression using the `boolean_parser`.
::

    >>> # import our database session and Model Class
    >>> from database.models import TableModel
    >>> from database import session
    >>>
    >>> # import the parser
    >>> from boolean_parser import parse

    >>> # create the parser and parse a sql condition
    >>> res = parse('table.x > 5 and table.y < 2')
    >>> res
    >>> and_(x>5, y<2)

Attached to our parsed results is a :py:meth:`boolean_parser.mixins.sqla.SQLAMixin.filter` method which accepts a list
of SQLAlchemy ORM Models as input.  It then traverses the parsed result, converting boolean operations, parameters names,
and conditional expressions into the appropriate relevant SQLAlchemy syntax.  The returned object is now a SQLAlchemy
object, usually a Boolean :py:class:`sqlalchemy.sql.expression.ClauseList`,
or a :py:class:`sqlalchemy.sql.expression.BinaryExpression`, objects that represent SQLalchemy filter clause elements.
::

    >>> # generate the sqlalchemy filter
    >>> ff = res.filter(TableModel)
    >>> type(ff)
    >>> sqlalchemy.sql.elements.BooleanClauseList

    >>> # display the SQLAlchemy filter
    >>> print(ff.compile(compile_kwargs={'literal_binds': True}))
    >>> table.x > 5 AND table.y < 2

You can pass the filter expression directly into the SQLAlchemy `filter` method during a query.
::

    >>> # perform the sqlalchemy query
    >>> session.query(TableModel).filter(ff).all()


Building a Custom Parser
------------------------


Clause Elements
---------------

``boolean_parser`` knows that the string "x > 3" is a condition and parses it correctly due to how the
conditional "clause" is defined using ``pyparsing``.  See :ref:`clauses` for more information
about the available clauses.
