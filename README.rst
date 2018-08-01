============================
EMDB-SFF Toolkit (``sfftk``)
============================

.. image:: https://badge.fury.io/py/sfftk.svg
    :target: https://badge.fury.io/py/sfftk

.. image:: https://travis-ci.org/emdb-empiar/sfftk.svg?branch=master
    :target: https://travis-ci.org/emdb-empiar/sfftk

.. image:: https://coveralls.io/repos/github/emdb-empiar/sfftk/badge.svg?branch=master
	:target: https://coveralls.io/github/emdb-empiar/sfftk?branch=master

.. image:: https://readthedocs.org/projects/sfftk/badge/?version=latest
	:target: http://sfftk.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status

.. contents::

Introduction
============

``sfftk`` is a set of utilities that facilitate creation, conversion and
modification of `Electron Microscopy Data Bank - Segmentation File Format
(EMDB-SFF) files <https://github.com/emdb-empiar/sfftk/tree/master/sfftk/test_data/sff>`_.
EMDB-SFF is an open, community-driven file format to handle annotated
segmentations and subtomogram averages that facilitates segmentation file
interchange. It is predominantly written in Python with some functionality
implemented as C-extensions for performance. It provides both a command-line
suite of commands and a Python API.