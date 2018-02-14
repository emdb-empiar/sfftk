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
def _random_float(): return random.random()


