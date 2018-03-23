#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_py

Unit tests for convert subcommand
"""
from __future__ import division

import glob
import os
import shlex
import unittest

import __init__ as tests
from .. import BASE_DIR
from .. import sff as Main
from ..core.parser import parse_args

__author__ = 'Paul K. Korir, PhD'
__email__ = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__ = '2016-06-10'
__updated__ = '2018-02-14'

user = 'test_user'
password = 'test'
host = 'localhost'
port = '4064'


class TestMain_handle_convert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def setUp(self):
        unittest.TestCase.setUp(self)
        #  clear all
        map(os.remove, glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff')))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        map(os.remove, glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff')))

    def test_seg(self):
        """Test that we can convert .seg"""
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.seg'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)

    def test_mod(self):
        """Test that we can convert .mod"""
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)

    def test_am(self):
        """Test that we can convert .am"""
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.am'),
            self.config_fn,
            )))
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)

    def test_surf(self):
        """Test that we can convert .surf"""
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.surf'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 1)

    def test_unknown(self):
        """Test that unknown fails"""
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.xxx'),
            self.config_fn,
        )))
        with self.assertRaises(ValueError):
            Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.sff'))
        self.assertEqual(len(sff_files), 0)

    def test_sff(self):
        """Test that we can convert .sff"""
        #  first convert from some other format e.g. .mod
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        # then convert to .hff
        args, configs = parse_args(shlex.split('convert {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)

    def test_hff(self):
        """Test that we can convert .hff"""
        #  first convert from some other format e.g. .mod
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.hff'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        # then convert to .sff
        args, configs = parse_args(shlex.split('convert {} -o {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.hff'),
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)

    def test_json(self):
        """Test that we can convert .json"""
        #  first convert from some other format e.g. .mod
        args, configs = parse_args(shlex.split('convert -o {} {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.json'),
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        # then convert to .sff
        args, configs = parse_args(shlex.split('convert {} -o {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'test_data.json'),
            os.path.join(tests.TEST_DATA_PATH, 'test_data.sff'),
            self.config_fn,
        )))
        Main.handle_convert(args, configs)
        sff_files = glob.glob(os.path.join(tests.TEST_DATA_PATH, '*.hff'))
        self.assertEqual(len(sff_files), 1)


"""
:TODO: view .hff, .json
"""


class TestMain_handle_view(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_read_am(self):
        """Test that we can view .am"""
        args, configs = parse_args(shlex.split('view {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.am'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_read_map(self):
        """Test that we can view .map"""
        args, configs = parse_args(shlex.split('view {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.map'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_read_mod(self):
        """Test that we can view .mod"""
        args, configs = parse_args(shlex.split('view {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_seg(self):
        """Test that we can view .seg"""
        args, configs = parse_args(shlex.split('view {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.seg'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_read_surf(self):
        """Test that we can view .surf"""
        args, configs = parse_args(shlex.split('view {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.surf'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_view(args, configs))

    def test_read_unknown(self):
        """Test that we cannot view unknown"""
        args, configs = parse_args(shlex.split('view {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.xxx'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_view(args, configs))


class TestMain_handle_notes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_list(self):
        """Test that we can list notes"""
        args, configs = parse_args(shlex.split('notes list {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_notes_list(args, configs))

    def test_show(self):
        """Test that we can list notes"""
        args, configs = parse_args(shlex.split('notes show -i 15559 {} --config-path {}'.format(
            os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff'),
            self.config_fn,
        )))
        self.assertEqual(0, Main.handle_notes_show(args, configs))

    def test_search(self):
        """Test that we can list notes"""
        args, configs = parse_args(shlex.split('notes search "mitochondria" --config-path {}'.format(self.config_fn)))
        self.assertEqual(0, Main.handle_notes_search(args, configs))
