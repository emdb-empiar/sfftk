#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

"""
test_py

Unit tests for convert subcommand
"""

__author__  = 'Paul K. Korir, PhD'
__email__   = 'pkorir@ebi.ac.uk'
__date__    = '2016-06-10'


import sys
import os
import glob
import unittest
import shlex

from ..core.parser import parse_args
import __init__ as tests
from .. import sff as Main

# sys.path.insert(0, "..")


# redirect sys.stderr/sys.stdout to /dev/null
# from: http://stackoverflow.com/questions/8522689/how-to-temporary-hide-stdout-or-stderr-while-running-a-unittest-in-python
_stderr = sys.stderr
_stdout = sys.stdout
null = open(os.devnull, 'wb')
sys.stdout = null
sys.stderr = null

user = 'test_user'
password = 'test'
host = 'localhost'
port = '4064'


class TestMain_handle_convert(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        # clear all 
        map(os.remove, glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff')))
         
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        map(os.remove, glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff')))
         
    def test_seg(self):
        """Test that we can convert .seg"""
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.seg')
            )))
        Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
         
    def test_mod(self):
        """Test that we can convert .mod"""
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod')
            )))
        Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
          
    def test_am(self):
        """Test that we can convert .am"""
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.am')
            )))
        Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
    def test_surf(self):
        """Test that we can convert .surf"""
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.surf')
            )))
        Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)
            
    def test_unknown(self):
        """Test that unknown fails"""
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.xxx')
            )))         
        with self.assertRaises(ValueError):
            Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 0)
     
    def test_sff(self):
        """Test that we can convert .sff"""
        # first convert from some other format e.g. .mod
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod')
            )))
        Main.handle_convert(args)
        # then convert to .hff
        args = parse_args(shlex.split('convert {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff')
            )))
        Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)

    def test_hff(self):
        """Test that we can convert .hff"""
        # first convert from some other format e.g. .mod
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.hff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod')
            )))
        Main.handle_convert(args)
        # then convert to .sff
        args = parse_args(shlex.split('convert {} -o {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.hff'),
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff')
            )))
        Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)

    def test_json(self):
        """Test that we can convert .json"""
        # first convert from some other format e.g. .mod
        args = parse_args(shlex.split('convert -o {} {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.json'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod')
            )))
        Main.handle_convert(args)
        # then convert to .sff
        args = parse_args(shlex.split('convert {} -o {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.json'),
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff')
            )))
        Main.handle_convert(args)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)
    

"""
:TODO: view .hff, .json
"""
 
class TestMain_handle_view(unittest.TestCase):
    def test_read_am(self):
        """Test that we can view .am"""
        args = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.am')
            )))
        self.assertEqual(0, Main.handle_view(args))
         
    def test_read_map(self):
        """Test that we can view .map"""
        args = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.map')
            )))
        self.assertEqual(0, Main.handle_view(args))
     
    def test_read_mod(self):
        """Test that we can view .mod"""
        args = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod')
            )))
        self.assertEqual(0, Main.handle_view(args))
    
    def test_seg(self):
        """Test that we can view .seg"""
        args = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.seg')
            )))
        self.assertEqual(0, Main.handle_view(args))
        
    def test_read_surf(self):
        """Test that we can view .surf"""
        args = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.surf')
            )))
        self.assertEqual(0, Main.handle_view(args))
         
    def test_read_unknown(self):
        """Test that we cannot view unknown"""
        args = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.xxx')
            )))
        self.assertEqual(0, Main.handle_view(args))


class TestMain_handle_notes(unittest.TestCase):
    def test_list(self):
        """Test that we can list notes"""
        args = parse_args(shlex.split('notes list {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff')
            )))
        self.assertEqual(0, Main.handle_notes_list(args))
    
    def test_show(self):
        """Test that we can list notes"""
        args = parse_args(shlex.split('notes show -i 15559 {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff')
            )))
        self.assertEqual(0, Main.handle_notes_show(args))
    
    def test_search(self):
        """Test that we can list notes"""
        args = parse_args(shlex.split('notes search "mitochondria"'))
        self.assertEqual(0, Main.handle_notes_search(args))
    
    
