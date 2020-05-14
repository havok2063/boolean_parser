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
                        value.setResultsName('value2'))
