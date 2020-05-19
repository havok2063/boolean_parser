
from __future__ import print_function, division, absolute_import

.. _clauses:

Clause Elements
===============

Clauses are elements of strings matching a specified syntax and can be any simple or complex string-matching
component. Clause elements are defined used the `pyparsing <https://pyparsing-docs.readthedocs.io>`_ syntax.
All clause definitions for ``boolean_parser`` are defined as exact string matches, and can be found
`here <https://github.com/havok2063/boolean_parser/blob/master/boolean_parser/clauses.py>`_.  A list of
currently available constructed clauses:

- :ref:`words <words>`: a simple word clause
- :ref:`conditions <conditions>`: a basic conditional expression clause
- :ref:`between_cond <conditions>`: a "between" conditional clause
- :ref:`fxn <functions>`: a generic function clause
- :ref:`fxn_cond <fxncond>`: a function used in a conditional expression
- :ref:`fxn_expr <fxnexpr>`: a function condition that uses a conditional expression

.. _words:

Words
-----

This clause represents a simple word matching any set of alphabet characters using the ``pyparsing.alphas``
group.  This clause has no purpose other than to serve as a test and/or building block for more complex clauses.
The following is an example parsing of a word clause:
::

    >>> from boolean_parser.clauses import words

    >>> # parse a string word
    >>> words.parseString('stuff').asDict()
    {'words': {'parameter': 'stuff'}}

.. _conditions:

Conditions
----------

These clauses are strings that represent a conditional expression often seen in logic, mathematics, or
programming, and match the following sytax **"parameter operand value"**, e.g. 'x > 1'.  An additional condition
is available for "between" expressions, e.g. "x between 2 and 3", using the syntax
**"parameter between value1 and value2"**.  The following
example highlights parsing of string conditions:
::

    >>> from boolean_parser.clauses import condition, between_cond

    >>> # parse a string condition
    >>> condition.parseString('x > 1').asDict()
    {'condition': {'parameter': 'x', 'operator': '>', 'value': '1'}

    >>> # parse a string between condition
    >>> condition.parseString('x between 3 and 5').asDict()
    {'between_condition': {'parameter': 'x', 'operator': 'between',
     'value1': '3', 'value2': '5'}}

.. _functions:

Functions
---------

Several clauses have been defined utilizing Python function syntax.  These clauses can be used if you want to parse
a string that identifies a Python function to be called and evaluted or to combine in a more complex operation.

Generic Functions
^^^^^^^^^^^^^^^^^

Use the `fxn` clause when you need to parse a generic function string that can handle parsing of optional function
arguments and keyword arguments.  This clause has the following syntax,
**"function(arg1, arg2, arg3, ..., kwarg1, kwarg2, kwarg3, ...)"**.  The syntax currently only supports arguments of
numeric or string types, and simple numeric, string, or boolean keyword arguments.  It currently does not support
iterable args/kwargs or the more general `*args, **kwargs` syntax.  The following examples highlight parsing of a
functional string.
::

    >>> from boolean_parser.clauses import fxn

    >>> # parse a generic function
    >>> example = 'test(1, 2, 3, hello, a=5, stuff=there, force_check=True)'
    >>> fxn.parseString(example).asDict()
    {'function': {'name': 'test',
     'args': ['1', '2', '3', 'hello'],
     'kwargs': {'a': '5', 'stuff': 'there', 'force_check': 'True'}}}

With optional arguments and keyword arguments:
::

    >>> # parse a function with only arguments
    >>> fxn.parseString('test(1, 2, 3, hello)').asDict()
    {'function': {'name': 'test', 'args': ['1', '2', '3', 'hello'], 'kwargs': ''}}

    >>> # parse a function with only keyword arguments
    >>> fxn.parseString('test(a=4, stuff=there, d=5)').asDict()
    {'function': {'name': 'test',
     'args': '',
     'kwargs': {'a': '4', 'stuff': 'there', 'd': '5'}}}

.. _fxncond:

Function Conditions
^^^^^^^^^^^^^^^^^^^

Use the ``fxn_cond`` clause when you have a general function that can be called and evaluated in a conditional
expression.  This clause has the syntax **"function() operand value"**, e.g. "test(1, 2, 3) > 5".  See the following
example of this type of clause:
::

    >>> fxn_cond.parseString('test(1,2,3) > 5').asDict()
    {'function_condition': {'function': {'name': 'test',
     'args': ['1', '2', '3'],
     'kwargs': ''},
     'operator': '>',
     'value': '5'}}

.. _fxnexpr:

Function Expressions
^^^^^^^^^^^^^^^^^^^^

Use the ``fxn_expr`` clause when you have a special function accepts as input a conditional expression, and
can be called and evaluated in a conditional expression as well.  This clause has the syntax
**"function(condition) operand value"**, e.g. "test(x > 1) <= 30".  The `condition` input to the function is a string
condition matching the above :ref:`conditions` syntax.  The following shows an example parsing of this clause:
::

    >>> fxn_expr.parseString('test(x > 1) <= 30').asDict()
    {'function_expression': {'function_call': {'name': 'test',
     'condition': {'parameter': 'x', 'operator': '>', 'value': '1'}},
     'operator': '<=',
     'value': '30'}}