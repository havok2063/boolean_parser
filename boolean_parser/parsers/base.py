# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: base.py
# Project: parsers
# Author: Brian Cherinka
# Created: Sunday, 17th February 2019 3:43:08 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Friday, 1st March 2019 2:18:11 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import copy
import six
import pyparsing as pp
from pyparsing import ParseException
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.clauses import condition, between_cond, words
from boolean_parser.actions.clause import Condition, Word


class BooleanParserException(Exception):
    pass


class Parser(object):
    ''' Core Parser class for parsing strings into objects

    A core Parser class that can parse strings into a set of objects
    based on a defined set of string clause elements, and actions to perform
    for each clause.
    '''
    _bools = [BoolNot, BoolAnd, BoolOr]
    _clauses = []
    _clause = None

    def __init__(self, value=None):
        self.original_input = value
        self._expression = None

        if self.original_input:
            self._expression = self.parse()

    @property
    def params(self):
        ''' The extracted parameters from the parsed string '''
        if isinstance(self._expression, Condition):
            return self._expression.fullname if self._expression else None
        return self._expression.params if self._expression else None

    @property
    def conditions(self):
        ''' The extracted conditions from the parsed string '''
        if isinstance(self._expression, Condition):
            return self._expression if self._expression else None
        return self._expression.conditions if self._expression else None

    def parse(self, value=None):
        ''' Parse a string conditional

        Calls ``parseString`` on the ``pyparsing`` clause element to parse the
        input string into a ``pyparsing.ParseResults`` object.

        Parameters:
            value: str
                The string expression to parse

        Returns:
            A pyparsing.ParseResults object

        Example:
            >>> from boolean_parser.parsers import Parser
            >>> pp = Parser()
            >>> pp.parse('x > 1')
            >>> x>1
        '''

        value = value or self.original_input
        assert value is not None, 'There must be some input to parse'
        assert isinstance(value, six.string_types), 'input must be a string'

        try:
            expression = self._parser.parseString(value)[0]
        except ParseException as e:
            raise BooleanParserException("Parsing syntax error ({0}) at line:{1}, "
                                         "col:{2}".format(e.markInputline(), e.lineno, e.col))
        else:
            self._expression = expression
            self.original_input = value
            return expression

    def __repr__(self):
        return f'<Parser(input="{self.original_input or ""}")>'

    @classmethod
    def build_parser(cls, clauses=None, actions=None, bools=None):
        ''' Builds a new boolean parser

        Constructs a new boolean Parser class given a set of clauses, actions,
        and boolean objects. Clauses are individual ``pyparsing`` elements that represent
        string clauses to pattern match on.  Actions are functions or classes set on each clause
        element that control how that clause is parsed.  See :ref:`clauses` for
        the available `pyparsing` clause elements.

        Assigns the default boolean classes, ``[BoolNot, BoolAnd, BoolOr]`` to the
        :py:func:`pyparsing.infixNotation` such that NOTs->ANDs->ORs.  If ``bools`` is
        specified instead, uses those object classes to handle boolean logic.  ``bools``
        must be a list of length 3 containing classes for boolean "not", "and", and "or" logic
        in that order.

        Parameters:
            clauses: list
                A list of pyparsing clause elements
            actions: list
                A list of actions to attach to each clause element
            bools: list
                A list of Boolean classes to use to handle boolean logic

        Example:
            >>> from boolean_parser.parsers import Parser
            >>> from boolean_parser.clauses import condition, words
            >>> from boolean_parser.actions.clause import Condition, Word
            >>>
            >>> # Assign the parsing order precedence for clauses
            >>> clauses = [condition, words]
            >>>
            >>> # Create a list of Actions for each clause in clauses
            >>> actions = [Condition, Word]
            >>>
            >>> # build the Parser with these clauses and actions
            >>> Parser.build_parser(clauses=clauses, actions=actions)
        '''

        # set clauses and actions
        clauses = clauses or cls._clauses
        assert clauses is not None, 'A list of clauses must be provided'
        cls.set_clauses(clauses)
        cls.build_clause()
        assert cls._clause is not None, 'A singular clause must be built from clauses'
        if actions:
            cls.set_parse_actions(clauses=clauses, actions=actions)

        # assign the combined clause to the recursive token pattern matcher
        where_exp = pp.Forward()
        where_exp <<= cls._clause

        # extract the Boolean precendent clauses
        bools = bools or cls._bools
        assert len(
            bools) == 3, 'there must be a set of "not, and, or" boolean precedent classes'
        bnot, band, bor = bools

        # build the expression parser
        cls._parser = pp.infixNotation(where_exp, [
            (pp.CaselessLiteral("not"), 1, pp.opAssoc.RIGHT, bnot),
            (pp.CaselessLiteral("and"), 2, pp.opAssoc.LEFT, band),
            (pp.CaselessLiteral("or"), 2, pp.opAssoc.LEFT, bor),
        ])

    @classmethod
    def set_parse_actions(cls, mapping=None, clauses=None, actions=None):
        ''' Attach actions to a pyparsing clause element

        ``pyparsing`` clause elements can have optional actions set with the
        ``setParseAction`` which control how each clause is parsed.  This maps a list
        of actions onto a list of clauses.  If ``mapping`` is used, it must be a list
        of tuples containing which action to map to which clause.  Otherwise
        ``clauses`` and ``actions`` must be provided as equal-length lists which contain,
        for each item, what action(s) to attach to the corresponding clause.

        Parameters:
            mapping: list of tuples
                A list of tuples containing a (clause, action) mapping.
            clauses: list
                A list of clauses
            actions: list
                A list of actions to attach to each clause

        Example:
            >>> from boolean_parser.parsers import Parser
            >>> from boolean_parser.clauses import condition, words
            >>> from boolean_parser.actions.clause import Condition, Word
            >>> clauses = [condition, words]
            >>> actions = [Condition, Word]
            >>> Parser.set_parse_actions(clauses=clauses, actions=actions)
        '''
        if not mapping:
            assert clauses and actions, 'clauses and actions must both be specified'
            assert isinstance(clauses, list), 'clauses must be a list'
            assert isinstance(actions, list), 'actions must be a list'
            assert len(clauses) == len(actions), 'clauses and actions must be the same length'
            mapping = zip(clauses, actions)
        else:
            assert isinstance(mapping, list), 'mapping must be a list'
            assert isinstance(mapping[0], (tuple, list)), 'mapping item must be a list or tuple'

        # requires clauses (a list)
        assert cls._clauses, 'class clauses must be set.  Call cls.set_clauses.'
        assert mapping is not None, 'a mapping between clauses and actions must be provided'

        # use reprs for list index check to bypass wonky list/equality clause comparisons
        clause_reprs = [repr(c) for c in cls._clauses]
        for item in mapping:
            clause, action = item
            assert repr(clause) in clause_reprs, 'clause must be included in list of class clauses'
            idx = clause_reprs.index(repr(clause))
            action = action if isinstance(action, (list, tuple)) else [action]
            cls._clauses[idx].setParseAction(*action)

    @classmethod
    def build_clause(cls, clauses=None):
        ''' Build a single clause from a list of clauses using pp.MatchFirst

        Merges a list of clauses into a single clause using :py:class:`pyparsing.MatchFirst`.
        This is equivalent to "clause = clause1 | clause2 | clause3`.  The clause precedence
        the Parser uses will be the order they appear in the list.  The default is to use
        the attached Parser._clauses list.

        Parameters:
            clauses: list
                A list of clauses to merge into a single clause
        '''
        clauses = clauses or cls._clauses
        assert isinstance(clauses, list), 'clauses must be a list'
        clauses = pp.MatchFirst(clauses)
        cls._clause = clauses

    @classmethod
    def set_clauses(cls, clauses):
        ''' Sets the list of clauses to use

        Parameters:
            clauses: list
                A list of clauses to attach to the Parser

        '''
        assert isinstance(clauses, list), 'clauses must be a list'
        cls._clauses = [copy.copy(c) for c in clauses]


# Set parse actions on conditions and build the Parser
clauses = [condition, between_cond, words]
actions = [Condition, Condition, Word]
Parser.build_parser(clauses=clauses, actions=actions)
