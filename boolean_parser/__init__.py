# !/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Filename: __init__.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Wednesday, 13th February 2019 1:15:25 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2019 Brian Cherinka
# Last Modified: Sunday, 17th February 2019 3:44:25 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import

from boolean_parser.parsers import Parser
from boolean_parser.parsers import SQLAParser


def parse(value, base='sqla'):
    ''' Convenience function to returned a parsed expression '''
    if base == 'base':
        return Parser(value).parse()
    elif base == 'sqla':
        return SQLAParser(value).parse()
    else:
        return Parser(value).parse()
        
