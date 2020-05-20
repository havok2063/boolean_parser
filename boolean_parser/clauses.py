# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: clauses.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Sunday, 17th February 2019 12:11:46 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 2:04:09 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import pyparsing as pp

# ------
# define base parser for words
word = pp.Word(pp.alphas).setResultsName('parameter')
words = pp.Group(word).setResultsName('words')

# ------
# define base parser for logical expressions
number = pp.Regex(r"[+-~]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")
name = pp.Word(pp.alphas + '._', pp.alphanums +
               '._').setResultsName('parameter')
operator = pp.oneOf(['==', '<=', '<', '>', '>=', '=', '!=',
                     '&', '|']).setResultsName('operator')
value = (pp.Word(pp.alphanums + '-_.*') | pp.QuotedString('"')
         | number).setResultsName('value')
condition = pp.Group(name + operator + value).setResultsName('condition')

# ------
# define base parser for between expression
between_cond = pp.Group(name + pp.CaselessLiteral('between').setResultsName('operator') +
                        value.setResultsName('value1') + pp.CaselessLiteral('and') +
                        value.setResultsName('value2')).setResultsName('between_condition')

# -------
# define base parser for functions
ppc = pp.pyparsing_common

# parantheses
LPAR = pp.Suppress('(')
RPAR = pp.Suppress(')')

# function arguments
arglist = pp.delimitedList(number | (pp.Word(pp.alphanums + '-_') + pp.NotAny('=')))
args = pp.Group(arglist).setResultsName('args')
# function keyword arguments
key = ppc.identifier() + pp.Suppress('=')
values = (number | pp.Word(pp.alphas))
keyval = pp.dictOf(key, values)
kwarglist = pp.delimitedList(keyval)
kwargs = pp.Group(kwarglist).setResultsName('kwargs')
# build generic function
fxn_args = args + ',' + kwargs | pp.Optional(args, default='') + pp.Optional(kwargs, default='')
fxn_name = (pp.Word(pp.alphas)).setResultsName('name')
fxn = pp.Group(fxn_name + LPAR + fxn_args + RPAR).setResultsName('function')

# fxn condition
fxn_cond = pp.Group(fxn + operator + value).setResultsName('function_condition')

# fxn conditional expression
function_call = pp.Group(fxn_name + LPAR + condition + RPAR).setResultsName('function_call')
fxn_expr = pp.Group(function_call + operator + value).setResultsName('function_expression')

# cone fxn conditions
#cone_cond = copy.copy(fxn)
#cone_cond.setParseAction(ConeCondition)

# histogram fxn conditions
#hist_cond = copy.copy(fxn)
#hist_cond.setParseAction(HistCondition)


# create a list of usable constructed clauses
available_clauses = [words, condition, between_cond, fxn, fxn_cond, fxn_expr]
