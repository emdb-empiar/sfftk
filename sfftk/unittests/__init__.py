# -*- coding: utf-8 -*-

# path to test data
from .. import test_data
TEST_DATA_PATH = test_data.__path__[0]

# helper functions
import random
def _random_integer(start=1, stop=1000): return random.randint(start, stop)
def _random_float(): return random.random()


