# boolean_parser

[![Build Status](https://travis-ci.com/havok2063/boolean_parser.svg?branch=master)](https://travis-ci.com/havok2063/boolean_parser)
[![Documentation Status](https://readthedocs.org/projects/boolean-parser/badge/?version=latest)](https://boolean-parser.readthedocs.io/en/latest/?badge=latest)
![Python application](https://github.com/havok2063/boolean_parser/workflows/Python%20application/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/havok2063/boolean_parser/badge.svg?branch=master)](https://coveralls.io/github/havok2063/boolean_parser?branch=master)
[![codecov](https://codecov.io/gh/havok2063/boolean_parser/branch/master/graph/badge.svg)](https://codecov.io/gh/havok2063/boolean_parser)


Python package for parsing a string with conditional expressions joined with boolean logic.  Uses the [pyparsing](https://github.com/pyparsing/pyparsing) package to construct grammatical clauses representing conditional expression, e.g. "x > 1 and y < 2".  String conditional expressions can then be parsed into object representation to be handled downstream.  Can
convert string boolean expressions into SQLAlchemy filter conditions.

Documentation: https://boolean-parser.readthedocs.io/en/latest/

Parsers:
 - Parser: core parser for handling parsing complex boolean conditional expressions
 - SQLParser: parser that enables converting a string conditional into a SQLAlchemy filter clause
