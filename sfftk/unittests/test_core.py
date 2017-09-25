# test_core.py
# -*- coding: utf-8 -*-
"""Unit tests for :py:mod:`sfftk.core` package"""

from __future__ import division

import os
import unittest

from ..core.print_tools import print_date


__author__      = "Paul K. Korir, PhD"
__email__       = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__        = "2017-05-15"


class TestCore_config(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sfftk
        cls.conf_file = os.path.join(sfftk.__path__[0], 'sff.conf')
    def test_read_config(self):
        """Test that we can read configs"""
        from ..core.configs import get_configs
        configs = get_configs(self.conf_file)
        self.assertEqual(configs['SFF_SCHEMA_PATH'], 'sff/schema')
        self.assertEqual(configs['SFF_SCHEMA_FILE'], 'emdb_sff.py')
        self.assertEqual(configs['__TEMP_FILE'], './temp-annotated.json')
        self.assertEqual(configs['__TEMP_FILE_REF'], '@')
    def test_write_config(self):
        """Test that we can write configs"""
        self.assertTrue(False)


class TestCore_print_utils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    def setUp(self):
        self.temp_fn = 'temp_file.txt'
        self.temp_file = open(self.temp_fn, 'w+')
    def tearDown(self):
        os.remove(self.temp_fn)
    def test_print_date_default(self):
        """Test default arguments for print_date(...)"""
        print_date("Test", stream=self.temp_file)
        self.temp_file.flush() # flush buffers
        self.temp_file.seek(0) # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertIn(_words[0], self._weekdays) # the first part is a date
        self.assertEqual(_words[-1][-1], '\n') # the last letter is a newline
    def test_print_date_no_newline(self):
        """Test that we lack a newline at the end"""
        print_date("Test", stream=self.temp_file, newline=False)
        self.temp_file.flush() # flush buffers
        self.temp_file.seek(0) # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertNotEqual(_words[-1][-1], '\n')
    def test_print_date_no_date(self):
        """Test that we lack a date at the beginning"""
        print_date("Test", stream=self.temp_file, incl_date=False)
        self.temp_file.flush() # flush buffers
        self.temp_file.seek(0) # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertNotIn(_words[0], self._weekdays) # the first part is a date


if __name__ == "__main__":
    unittest.main()