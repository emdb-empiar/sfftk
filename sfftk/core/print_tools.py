#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
print_tools.py
==============

Utilities for printing stuff to the screen.
"""
from __future__ import division, print_function

import sys
import time

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk'
__date__ = '2016-16-06'
__updated__ = '2018-02-14'


def print_date(print_string, stream=sys.stderr, newline=True, incl_date=True):
    """Print the given string with date on the given stream
    
    :param str print_string: the string to be printed
    :param stream: the stream to write to
    :type stream: `sys.stderr` or `sys.stdout`
    :param bool newline: whether (default) or not to add a newline at the end
    """
    if newline:
        if incl_date:
            print("%s\t%s" % (time.ctime(time.time()), print_string), file=stream)
        else:
            print("%s" % (print_string), file=stream)
    else:
        if incl_date:
            print("%s\t%s" % (time.ctime(time.time()), print_string), file=stream, end='')
        else:
            print("%s" % (print_string), file=stream, end='')


def get_printable_ascii_string(s):
    """Given a string of ASCII and non-ASCII return the maximal substring with a printable ASCII prefix.
    
    :param str s: the string to search
    :return str ascii_s: the minimal ASCII string
    """
    # get the list of ordinals
    s_ord = map(ord, s)
    # ASCII have ordinals on 0-127
    # get the first non-printable ASCII i.e. 32 < ord > 127
    try:
        non_ascii = filter(lambda x: x < 32 or x > 127, s_ord)[0]
    except IndexError:
        return ''
    # get the index along the string where this character exists
    non_ascii_index = s_ord.index(non_ascii)
    # return the prefix upto and excluding the first non-ASCII
    ascii_s = s[:non_ascii_index]
    return ascii_s


def print_static(print_string, stream=sys.stderr, incl_date=True):
    """Print the given string with date on the given stream from the first position 
    overwriting any characters. 
    
    This is a useful way to display progress without overcrowding the screen.
    
    :param str print_string: the string to be printed
    :param stream: the stream to write to
    :type stream: `sys.stderr` or `sys.stdout`
    :param bool newline: whether (default) or not to add a newline at the end
    """
    try:
        assert stream is sys.stderr or stream is sys.stdout
    except:
        print(
            "Invalid stream '{}'; should be Python objects `sys.stderr` or `sys.stdout`".format(stream),
            file=sys.stderr
        )

    if incl_date:
        print("\r%s\t%s" % (time.ctime(time.time()), print_string), file=stream, end='')
    else:
        print("\r%s" % (print_string), file=stream, end='')
