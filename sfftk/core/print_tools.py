#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
print_tools.py
==============

Utilities for printing stuff to the screen.
"""
from __future__ import division, print_function

import string
import sys
import time

from ..core import _basestring, _bytes, _decode, _encode

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk'
__date__ = '2016-16-06'
__updated__ = '2018-02-14'


def print_date(print_string, stream=sys.stderr, newline=True, incl_date=True):
    """Print the given string with date on the given stream
    
    :param print_string: the bytes/str to be printed
    :type print_string: bytes or str
    :param stream: the stream/file to write to
    :type stream: :py:obj:`sys.stderr` or :py:obj:`sys.stdout`
    :param bool newline: whether (default) or not to add a newline at the end
    :param bool incl_date: whether (default) or not to include the date at the beginning
    """
    try:
        assert isinstance(print_string, _basestring)
    except AssertionError:
        raise ValueError(u"input should be subclass of basestring: str or unicode")
    if isinstance(print_string, _bytes):
        print_string = _decode(print_string, 'utf-8')
    if newline:
        if incl_date:
            print(u"%s\t%s" % (time.ctime(time.time()), print_string), file=stream)
        else:
            print(u"%s" % (print_string), file=stream)
    else:
        if incl_date:
            print(u"%s\t%s" % (time.ctime(time.time()), print_string), file=stream, end='')
        else:
            print(u"%s" % (print_string), file=stream, end='')


def get_printable_ascii_string(B):
    """Given a bytes string of ASCII and non-ASCII return the maximal printable prefix
    
    :param bytes B: the bytes string to search
    :return ascii_b: the maximal ASCII prefix
    :rtype: bytes
    """
    B = _encode(B, 'utf-8')
    printables = list(map(ord, string.printable))
    index = len(B) - 1
    if sys.version_info[0] > 2:
        for i, b in enumerate(B): # for each byte
            if b not in printables:
                index = i
                break
    else:
        for i, b in enumerate(B): # for each byte
            _b = ord(b)
            if _b not in printables:
                index = i
                break
    ascii_b = B[:index]
    return ascii_b


def print_static(print_string, stream=sys.stderr, incl_date=True):
    """Print the given string with date on the given stream from the first position 
    overwriting any characters. 
    
    This is a useful way to display progress without overcrowding the screen.
    
    :param print_string: the bytes/str to be printed
    :type print_string: bytes or str
    :param stream: the stream/file to write to
    :type stream: :py:obj:`sys.stderr` or :py:obj:`sys.stdout`
    :param bool incl_date: whether (default) or not to include the date at the beginning
    """
    try:
        assert isinstance(print_string, _basestring)
    except AssertionError:
        raise ValueError(u"input should be subclass of basestring: str or unicode")
    print_string = _decode(print_string, 'utf-8')
    if incl_date:
        print(u"\r{}\t{}".format(time.ctime(time.time()), print_string), file=stream, end='')
    else:
        print(u"\r{}".format(print_string), file=stream, end='')
