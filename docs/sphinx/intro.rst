
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

The parsed result is a :py:class:`boolean_parser.actions.clause.Condition` object containing extracted
information about the condition.   The `data` attribute contains a dictionary of all relevant information,
while the parameter name, operand, and value are available as attributes on the ``Condition`` class.
::

    >>> # show the extracted data
    >>> res.data
    {'parameter': 'x', 'operator': '>', 'value': '3'}

    >>> print(res.name, res.operator, res.value)
    x > 3

``boolean_parser`` knows that the string "x > 3" is a condition and parses it correctly due to how the
conditional "clause" is defined using ``pyparsing`` grammer constructors.  See :ref:`clauses` for more information
about the available clauses in ``boolean_parser``.

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

The :py:func:`boolean_parser.parse` convenience function is essentially a wrapper around the ``Parser`` classes
in :py:mod:`boolean_parser.parsers`.  The base parser is :py:class:`boolean_parser.parsers.base.Parser`.  The default
parser used by the ``parse`` convenience function is the :py:class:`boolean_parser.parsers.sqla.SQLAParser`.  To change
the parser used by the function, set the ``base`` keyword argument.
::

    >>> # use the default SQLAlchemy Parser
    >>> res = parse('x > 1')

    >>> # use the core base Parser
    >>> res = parse('x > 1', base='base')

You can also interact with the ``Parser`` class directly.
::

    >>> from boolean_parser.parsers import Parser
    >>> pp = Parser('x > 1')

To parse the input string expression, use the ``parse`` method, which performs exactly the same as the ``parse``
convenience function.
::

    >>> # parse the expression
    >>> res = pp.parse()
    >>> res
    x>1

The original input string expression, as well as the extracted parameters and conditions are accessible via the
``original_input``, ``params``, and ``conditions`` attributes, respectively.
::

    >>> pp.original_input
    'x > 1'

    >>> pp.params
    x

    >>> pp.conditions
    x>1


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

A custom parser can be built by passing in a list of ``pyparsing`` clause elements, and optional clause actions,
into the ``build_parser`` class method of the base ``Parser`` class.  Let's look at an example of
how to build a parser to parse a simple street name.  We'll break this example down in the following subsections.
::

    >>> # import the base Parser class
    >>> from boolean_parser.parsers import Parser

    >>> # define the address clause element with pyparsing grammar constructors
    >>> import pyparsing as pp
    >>> snumber = pp.Word(pp.nums).setResultsName('street_number')
    >>> sname = pp.Word(pp.alphas).setResultsName('street_name')
    >>> stype = pp.oneOf(['street', 'avenue', 'circle']).setResultsName('street_type')
    >>> street = pp.Group(snumber + sname + stype).setResultsName('street')

    >>> # rebuild the Parser with the new street clause
    >>> Parser.build_parser(clauses=[street])

    >>> parser = Parser()
    >>> res = parser.parse('2525 redwood street')
    >>> res.asDict()
    {'street_number': '2525', 'street_name': 'redwood', 'street_type': 'street'}

Clause Elements
^^^^^^^^^^^^^^^

Clause elements are defined using `pyparsing grammar constructors <https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html#basic-parserelement-subclasses>`_.
Clause elements are best defined from the bottom up, starting with the most simple structures and grouping them together.
Street names can be broken down into the syntax **"street_number street_name street_type"**.  Let's define
each component and build our "street" clause element.
::

    >>> import pyparsing as pp

    >>> # define a street number as a "word" of any combination of digits 0-9
    >>> snumber = pp.Word(pp.nums).setResultsName('street_number')

    >>> # define the street name as a "word" of any combination of alphabet characters
    >>> sname = pp.Word(pp.alphas).setResultsName('street_name')

    >>> # define the type of street as one option in a set of choices
    >>> stype = pp.oneOf(['street', 'avenue', 'circle']).setResultsName('street_type')

    >>> # group the components together into a final street clause element
    >>> street = pp.Group(snumber + sname + stype).setResultsName('street')

We use the :py:meth:`pyparsing.ParserElement.setResultsName` to assign a label to each component.  This helps break up
complex clauses into easily identifable components, and allows us to use the :py:meth:`pyparsing.ParseResults.asDict`
method to create a dictionary of named parameters.  The :py:meth:`pyparsing.ParserElement.parseString` method is the
recommended way of parsing a string.
::

    >>> street.parseString('2 blue avenue').asDict()
    {'street': {'street_number': '2',
     'street_name': 'blue',
     'street_type': 'avenue'}}

Build the new Parser
^^^^^^^^^^^^^^^^^^^^

Now that we have a clause defined, we can use the ``build_parser`` class method on ``Parser`` to contruct a new parser
class capable of parsing street names. We pass in the ``street`` clause as a list input to the ``clauses`` keyword
argument.
::

    >>> # rebuild the Parser with the new street clause
    >>> Parser.build_parser(clauses=[street])

Now we instantiate our new parser and call ``parse`` on any input "street" string.
::

    >>> parser = Parser()
    >>> res = parser.parse('2525 redwood street')
    >>> res.asDict()
    {'street_number': '2525', 'street_name': 'redwood', 'street_type': 'street'}

    >>> res = parser.parse('2 blue avenue')
    >>> res.asDict()
    {'street_number': '2', 'street_name': 'blue', 'street_type': 'avenue'}

Clause Precendence
^^^^^^^^^^^^^^^^^^

The clauses input to ``build_parser`` can be a list of any number of constructed clause elements.  These clauses
are combined into a single clause using :py:func:`pyparsing.MatchFirst` which combines clauses with "ORS", i.e.
"clause1 | clause2 | clause3".  ``MatchFirst`` will parse and return the first string match it finds that matches one
of the input clauses.
::

    >>> from boolean_parser.parsers import Parser
    >>> from boolean_parser.clauses import words

    >>> # build a parser with the street and built-in words clauses
    >>> Parser.build_parser(clauses=[street, words])
    >>> parser = Parser()

    >>> # the first parser match is a street
    >>> parser.parse('2 blue avenue hammer')
    (['2', 'blue', 'avenue'], {'street_number': ['2'], 'street_name': ['blue'], 'street_type': ['avenue']})

    >>> # the first parser match is a word
    >>> parser.parse('hammer 2 blue avenue')
    (['hammer'], {'parameter': ['hammer']})


Parse Actions
^^^^^^^^^^^^^

"Parsing Actions" are actions to be performed on a clause element after a successful parsed match.  One or more
actions can be assigned to each clause element.  When you build a parser, by default there are no special actions
applied and the parser returns a standard :py:class:`pyparsing.ParseResults`object. This can be overridden by
providing the ``actions`` keyword argument with a list of actions to assign to each clause elements.  The list
of ``actions`` must be of equal length to the input list of ``clauses``.  Actions can be any callable.  Let's
define a function action that prints the street name during parsing.
::

    >>> define the action function
    >>> def print_name(data):
    >>>    print('The street_name is:', data[0].asDict()['street_name'])

    >>> Parser.build_parser(clauses=[e], actions=[print_name])
    >>> parser = Parser()
    The street_name is: blue
    (['2', 'blue', 'avenue'], {'street_number': ['2'], 'street_name': ['blue'], 'street_type': ['avenue']})

When passing in actions to ``build_parser``, it calls :py:meth:`pyparsing.ParserElement.setParseAction` to assign that
action to the relevant clause element.  We can also define more complex action classes and combine multiple
actions together.  Let's define a ``Street`` class that handles the parsed result.  When we pass this class in
as an action, the parser will return a new instance of ``Street`` as the parsed result.  Actions for a single clause
element can be chained together by passing in a list or tuple of actions for each clause element.  Let's add the
`Street` action to the `print_name` action.
::

    >>> define the action class
    >>> class Street(object):
    >>>     def __init__(self, data):
    >>>         dd = data[0].asDict()
    >>>         self.name = dd['street_name']
    >>>         self.number = dd['street_number']
    >>>         self.type = dd['street_type']
    >>>     def __repr__(self):
    >>>         return f'<Street ({self.number} {self.name} {self.type})>'

    >>> Parser.build_parser(clauses=[e], actions=[[print_name, Street]])
    >>> parser = Parser()
    >>> parser.parse('2 blue avenue')
    The street_name is: blue
    <Street (2 blue avenue)>

Boolean Joins
^^^^^^^^^^^^^

The base ``Parser`` class by default contains boolean operator precedence in the order of NOTS-> ANDS-> ORS.  The
default boolean classes uses can be overridden by providing a list of boolean class objects to the ``bools`` keyword
argument.  These classes will be used to provide the boolean logic and must be in the same order of [nots, ands, ors].
::

    >>> res = parser.parse('2525 redwood street and 34 blue avenue')
    The street_name is: redwood
    The street_name is: blue
    >>> res
    and_(<Street (2525 redwood street)>, <Street (34 blue avenue)>)

    >>> type(res)
    boolean_parser.actions.boolean.BoolAnd

    >>> res.conditions[0]
    <Street (2525 redwood street)>

    >>> res.conditions[1]
    <Street (34 blue avenue)>

