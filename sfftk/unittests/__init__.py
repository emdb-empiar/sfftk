# -*- coding: utf-8 -*-
import os
import random

from .. import BASE_DIR

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-06-15'
__updated__ = '2018-02-14'

# path to test data
TEST_DATA_PATH = os.path.join(BASE_DIR, 'test_data')


# helper functions
def _random_integer(start=1, stop=1000): return random.randint(start, stop)


def _random_float(multiplier=1): return random.random() * multiplier


def _random_integers(count=10, start=1, stop=1000, as_string=False, sep=' '):
    if as_string:
        return sep.join(map(str, [_random_integer(start=start, stop=stop) for _ in xrange(count)]))
    else:
        return [_random_integer(start=start, stop=stop) for _ in xrange(count)]


def _random_floats(count=10, multiplier=1):
    return [_random_float(multipler=multiplier) for _ in xrange(count)]
