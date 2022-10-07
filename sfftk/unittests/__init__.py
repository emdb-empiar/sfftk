import os
import random
import sys
from unittest import TestCase

from sfftkrw.core import _xrange

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
        return sep.join(map(str, [_random_integer(start=start, stop=stop) for _ in _xrange(count)]))
    else:
        return [_random_integer(start=start, stop=stop) for _ in _xrange(count)]


def _random_floats(count=10, multiplier=1):
    return [_random_float(multiplier=multiplier) for _ in _xrange(count)]


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class Py23Fix(object):
    def __init__(self, *args, **kwargs):
        if sys.version_info[0] > 2:
            pass
        else:
            # new names for assert methods
            self.assertCountEqual = self.assertItemsEqual
            self.assertRegex = self.assertRegexpMatches
            self.assertRaisesRegex = self.assertRaisesRegexp
        super(Py23Fix, self).__init__(*args, **kwargs)


class Py23FixTestCase(Py23Fix, TestCase):
    """Mixin to fix method changes in TestCase class"""
