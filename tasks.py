# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Filename: tasks.py
# Project: boolean_parser
# Author: Brian Cherinka
# Created: Thursday, 9th April 2020 5:10:09 pm
# License: BSD 3-clause "New" or "Revised" License
# Copyright (c) 2020 Brian Cherinka
# Last Modified: Thursday, 9th April 2020 5:39:45 pm
# Modified By: Brian Cherinka


from __future__ import print_function, division, absolute_import
import os

from invoke import Collection, task


# This file contains tasks that can be easily run from the shell terminal using the Invoke
# python package. If you do not have invoke, install it with pip install
# To list the tasks available, type invoke --list from the top-level repo directory

@task
def clean_docs(ctx, target=None):
    """Cleans up the docs."""

    if target is None:
        target = ctx.sphinx.target

    print('Cleaning the docs')
    ctx.run(f'rm -rf {target}/_build')


@task
def build_docs(ctx, target=None, clean=False):
    """Builds the Sphinx docs"""

    if target is None:
        target = ctx.sphinx.target

    if clean:
        print('Cleaning the docs')
        ctx.run(f'rm -rf {target}/_build', pty=True)

    print('Building the docs')
    os.chdir(f'{target}')
    ctx.run('make html', pty=True)


@task
def show_docs(ctx, target=None):
    """Shows the Sphinx docs"""

    if target is None:
        target = ctx.sphinx.target

    print('Showing the docs')
    os.chdir(f'{target}/_build/html')
    ctx.run('open ./index.html')


@task
def clean(ctx):
    """Cleans up build files and test files."""

    print('Cleaning')
    ctx.run('rm -rf htmlcov **/htmlcov .coverage* **/.coverage*')
    ctx.run('rm -rf build')
    ctx.run('rm -rf dist')
    ctx.run('rm -rf **/*.egg-info *.egg-info')


@task(clean)
def deploy(ctx, repo=None):
    """ Deploy the project to PyPI

    Can specify a custom repo defined in your .pypirc file with the
    repo keyword. Default is to deploy to standard pypi index.

    Parameters:
        repo (str):
            The pypi repo index to upload to.  Defined in .pypirc file.
    """

    if repo is False:
        print('Deploying to sdss PyPI!')
        repository = ''
    else:
        print('Deploying to alternate PyPI!')
        repository = f'-r {repo}'

    ctx.run('python setup.py sdist bdist_wheel --universal')
    ctx.run(f'twine upload {repository} dist/*')


# create a collection of tasks
ns = Collection(clean, deploy)

# create a sub-collection for the doc tasks
docs = Collection('docs')
docs.add_task(build_docs, 'build')
docs.add_task(clean_docs, 'clean')
docs.add_task(show_docs, 'show')
ns.add_collection(docs)

ns.configure({'sphinx': {'target': 'docs/sphinx'}})
