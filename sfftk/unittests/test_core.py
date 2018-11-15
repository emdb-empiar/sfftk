# -*- coding: utf-8 -*-
# test_core.py
"""Unit tests for :py:mod:`sfftk.core` package"""
from __future__ import division, print_function

import glob
import os
import random
import shlex
import sys
import unittest
import numpy
import shutil
from stl import Mesh


from . import TEST_DATA_PATH, _random_integer, _random_integers, _random_float, _random_floats, isclose
from .. import BASE_DIR
from ..core import utils
from ..core.configs import Configs, get_config_file_path, load_configs, \
    get_configs, set_configs, del_configs
from ..core.parser import Parser, parse_args
from ..core.print_tools import print_date
from ..core.prep import bin_map, transform_stl_mesh, construct_transformation_matrix
from ..notes import RESOURCE_LIST

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-05-15"


class TestCoreConfigs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_configs = os.path.expanduser("~/.sfftk/sff.conf")
        cls.user_configs_hide = os.path.expanduser("~/.sfftk/sff.conf.test")
        cls.dummy_configs = os.path.expanduser("~/sff.conf.test")
        cls.test_config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'test_sff.conf')
        cls.config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'sff.conf')
        cls.config_values = {
            '__TEMP_FILE': './temp-annotated.json',
            '__TEMP_FILE_REF': '@',
        }

    @classmethod
    def tearDownClass(cls):
        pass

    def load_values(self):
        """Load config values into test config file"""
        with open(self.config_fn, 'w') as f:
            for n, v in self.config_values.iteritems():
                f.write('{}={}\n'.format(n, v))

    def clear_values(self):
        """Empty test config file"""
        with open(self.config_fn, 'w') as _:
            pass

    def setUp(self):
        self.load_values()

    def tearDown(self):
        self.clear_values()

    def move_user_configs(self):
        # when running this test we need to hide ~/.sfftk/sff.conf if it exists
        # we move ~/.sfftk/sff.conf to ~/.sfftk/sff.conf.orig
        # then move it back once the test ends
        # if the test does not complete we will have to manually copy it back
        # ~/.sfftk/sff.conf.orig to ~/.sfftk/sff
        if os.path.exists(self.user_configs):
            shutil.move(
                self.user_configs,
                self.user_configs_hide,
            )

    def return_user_configs(self):
        # we move back ~/.sfftk/sff.conf.orig to ~/.sfftk/sff.conf
        if os.path.exists(self.user_configs_hide):
            shutil.move(
                self.user_configs_hide,
                self.user_configs,
            )

    def make_dummy_user_configs(self, param='TEST', value='TEST_VALUE'):
        if os.path.exists(self.user_configs):
            self.move_user_configs()
        with open(self.user_configs, 'w') as c:
            c.write("{}={}\n".format(param, value))

    def remove_dummy_user_configs(self):
        os.remove(self.user_configs)
        self.return_user_configs()

    def make_dummy_configs(self, param='TEST_CONFIG', value='TEST_CONFIG_VALUE'):
        with open(self.dummy_configs, 'w') as c:
            c.write("{}={}\n".format(param, value))

    def remove_dummy_configs(self):
        os.remove(self.dummy_configs)

    def test_default_ro(self):
        """Test that on a fresh install we use shipped configs for get"""
        self.move_user_configs()
        args = Parser.parse_args(shlex.split("config get --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == Configs.shipped_configs)
        self.return_user_configs()

    def test_user_configs_ro(self):
        """Test that if we have user configs we get them"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config get --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.remove_dummy_user_configs()

    def test_shipped_default(self):
        """Test that we get shipped and nothing else when we ask for them"""
        self.move_user_configs()
        args = Parser.parse_args(shlex.split("config get --shipped-configs --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, Configs.shipped_configs)
        self.return_user_configs()

    def test_shipped_user_configs_exist_ro(self):
        """Test that even if user configs exist we can only get shipped configs"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config get --shipped-configs --all"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, Configs.shipped_configs)
        self.remove_dummy_user_configs()

    def test_config_path_default_ro(self):
        """Test that we can get configs from some path"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config get --config-path {} --all".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_user_configs()

    def test_config_path_over_shipped_ro(self):
        """Test that we use config path even if shipped specified"""
        self.move_user_configs()
        self.make_dummy_user_configs()
        args = Parser.parse_args(
            shlex.split("config get --config-path {} --shipped-configs --all".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_user_configs()
        self.return_user_configs()

    def test_default_rw(self):
        """Test that when we try to write configs on a fresh install we get user configs"""
        self.move_user_configs()
        args = Parser.parse_args(shlex.split("config set A B"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.assertTrue(os.path.exists(self.user_configs))
        self.return_user_configs()

    def test_user_configs_rw(self):
        """Test that if we have user configs we can set to them"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("config set A B"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.remove_dummy_user_configs()

    def test_shipped_default_rw(self):
        """Test that we cannot write to shipped configs"""
        self.move_user_configs()
        args = Parser.parse_args(shlex.split("config set --shipped-configs A B"))
        config_file_path = get_config_file_path(args)
        self.assertIsNone(config_file_path)
        self.return_user_configs()

    def test_config_path_default_rw(self):
        """Test that we can get configs from some path"""
        self.make_dummy_configs()
        args = Parser.parse_args(shlex.split("config set --config-path {} A B".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()

    def test_config_path_over_shipped_rw(self):
        """Test that we use config path even if shipped specified"""
        self.move_user_configs()
        self.make_dummy_configs()
        args = Parser.parse_args(
            shlex.split("config set --config-path {} --shipped-configs A B".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()
        self.return_user_configs()

    def test_default_other(self):
        """Test that all non-config commands on a fresh install use shipped configs"""
        self.move_user_configs()
        args = Parser.parse_args(shlex.split("view file.json"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == Configs.shipped_configs)
        self.assertFalse(os.path.exists(self.user_configs))
        self.return_user_configs()

    def test_user_configs_other(self):
        """Test that if we have user configs we can set to them"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("view file.json"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == self.user_configs)
        self.remove_dummy_user_configs()

    def test_shipped_default_other(self):
        """Test that we cannot write to shipped configs even if we have user configs"""
        self.make_dummy_user_configs()
        args = Parser.parse_args(shlex.split("view file.json --shipped-configs"))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path == Configs.shipped_configs)
        self.remove_dummy_user_configs()

    def test_config_path_default_other(self):
        """Test that we can get configs from some path"""
        self.make_dummy_configs()
        args = Parser.parse_args(shlex.split("view --config-path {} file.json".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()

    def test_config_path_over_shipped_other(self):
        """Test that we use config path even if shipped specified"""
        self.move_user_configs()
        self.make_dummy_configs()
        args = Parser.parse_args(
            shlex.split("view --config-path {} --shipped-configs file.json".format(self.dummy_configs)))
        config_file_path = get_config_file_path(args)
        self.assertTrue(config_file_path, self.dummy_configs)
        self.remove_dummy_configs()
        self.return_user_configs()

    def test_load_shipped(self):
        """Test that we actually load shipped configs"""
        self.move_user_configs()
        args, configs = parse_args(shlex.split("view file.json"))
        # user configs should not exist
        self.assertFalse(os.path.exists(os.path.expanduser("~/.sfftk/sff.conf")))
        self.assertEqual(configs['__TEMP_FILE'], './temp-annotated.json')
        self.assertEqual(configs['__TEMP_FILE_REF'], '@')
        self.return_user_configs()

    def test_config_path(self):
        """Test that we can read configs from config path"""
        args, configs = parse_args(shlex.split('view --config-path {} file.sff'.format(self.test_config_fn)))
        self.assertEqual(configs['HAPPY'], 'DAYS')

    def test_user_config(self):
        """Test that we can read user configs from ~/.sfftk/sff.conf"""
        self.move_user_configs()
        # no user configs yet
        self.assertFalse(os.path.exists(os.path.expanduser("~/.sfftk/sff.conf")))
        # set a custom value to ensure it's present in user configs
        args, configs = parse_args(shlex.split('config set --force NAME VALUE'))
        set_configs(args, configs)
        # now user configs should exist
        self.assertTrue(os.path.exists(os.path.expanduser("~/.sfftk/sff.conf")))
        args, configs = parse_args(shlex.split('view file.sff'))
        self.assertEqual(configs['NAME'], 'VALUE')
        self.return_user_configs()

    def test_precedence_config_path(self):
        """Test that config path takes precedence"""
        # set a custom value to ensure it's present in user configs
        args, configs = parse_args(shlex.split('config set --force NAME VALUE'))
        set_configs(args, configs)
        args, configs = parse_args(
            shlex.split('view --config-path {} --shipped-configs file.sff'.format(self.test_config_fn)))
        self.assertEqual(configs['HAPPY'], 'DAYS')

    def test_precedence_shipped_configs(self):
        """Test that shipped configs, when specified, take precedence over user configs"""
        # set a custom value to ensure it's present in user configs
        args, configs = parse_args(shlex.split('config set --force NAME VALUE'))
        set_configs(args, configs)
        args, configs = parse_args(shlex.split('view file.sff --shipped-configs'))
        self.assertEqual(configs['__TEMP_FILE'], './temp-annotated.json')
        self.assertEqual(configs['__TEMP_FILE_REF'], '@')
        self.assertNotIn('NAME', configs)

    def test_get_configs(self):
        """Test that we can get a config by name"""
        self.move_user_configs()
        args, configs = parse_args(shlex.split('config get __TEMP_FILE --config-path {}'.format(self.config_fn)))
        print(configs)
        self.assertTrue(get_configs(args, configs) == os.EX_OK)
        self.return_user_configs()

    def test_get_all_configs(self):
        """Test that we can list all configs"""
        self.move_user_configs()
        args, configs = parse_args(shlex.split('config get --all --config-path {}'.format(self.config_fn)))
        self.assertTrue(get_configs(args, configs) == os.EX_OK)
        self.assertTrue(len(configs) > 0)
        self.return_user_configs()

    def test_get_absent_configs(self):
        """Test that we are notified when a config is not found"""
        self.move_user_configs()
        args, configs = parse_args(shlex.split('config get alsdjf;laksjflk --config-path {}'.format(self.config_fn)))
        self.assertTrue(get_configs(args, configs) == 1)
        self.return_user_configs()

    def test_set_configs(self):
        """Test that we can set configs"""
        self.move_user_configs()
        args, configs_before = parse_args(
            shlex.split('config set --force NAME VALUE --config-path {}'.format(self.config_fn)))
        len_configs_before = len(configs_before)
        self.assertTrue(set_configs(args, configs_before) == 0)
        _, configs_after = parse_args(shlex.split('config get alsdjf;laksjflk --config-path {}'.format(self.config_fn)))
        len_configs_after = len(configs_after)
        self.assertTrue(len_configs_before < len_configs_after)
        self.return_user_configs()

    def test_set_new_configs(self):
        """Test that new configs will by default be written to user configs .i.e. ~/sfftk/sff.conf"""
        self.move_user_configs()
        args, configs = parse_args(shlex.split('config set --force NAME VALUE'))
        self.assertTrue(set_configs(args, configs) == os.EX_OK)
        _, configs = parse_args(shlex.split('config get --all'))
        self.assertDictContainsSubset({'NAME': 'VALUE'}, configs)
        self.return_user_configs()

    def test_set_force_configs(self):
        """Test that forcing works"""
        self.move_user_configs()
        args, configs = parse_args(shlex.split('config set --force NAME VALUE'))
        self.assertTrue(set_configs(args, configs) == os.EX_OK)
        self.assertTrue(configs['NAME'] == 'VALUE')
        args, configs_after = parse_args(shlex.split('config set --force NAME VALUE1'))
        self.assertTrue(set_configs(args, configs_after) == os.EX_OK)
        self.assertTrue(configs_after['NAME'] == 'VALUE1')
        self.return_user_configs()

    def test_del_configs(self):
        """Test that we can delete configs"""
        self.move_user_configs()
        # first we get current configs
        args, configs = parse_args(shlex.split('config set --force NAME VALUE --config-path {}'.format(self.config_fn)))
        # then we set an additional config
        self.assertTrue(set_configs(args, configs) == 0)
        # then we delete the config
        args, configs_before = parse_args(
            shlex.split('config del --force NAME  --config-path {}'.format(self.config_fn)))
        len_configs_before = len(configs_before)
        self.assertTrue(del_configs(args, configs_before) == 0)
        args, configs_after = parse_args(shlex.split('config get --all --config-path {}'.format(self.config_fn)))
        len_configs_after = len(configs_after)
        self.assertTrue(len_configs_before > len_configs_after)
        self.return_user_configs()

    def test_del_all_configs(self):
        """Test that we can delete all configs"""
        self.move_user_configs()
        args, configs = parse_args(shlex.split('config del --force --all --config-path {}'.format(self.config_fn)))
        self.assertTrue(del_configs(args, configs) == 0)
        _, configs = parse_args(shlex.split('config get --all --config-path {}'.format(self.config_fn)))
        self.assertTrue(len(configs) == 0)
        self.return_user_configs()

    def test_write_shipped_fails(self):
        """Test that we cannot save to shipped configs"""
        self.move_user_configs()
        args, configs = parse_args(
            shlex.split('config set --force NAME VALUE --config-path {}'.format(os.path.join(BASE_DIR, 'sff.conf'))))
        self.assertTrue(set_configs(args, configs) == 1)
        self.return_user_configs()


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
        self.temp_file.flush()  # flush buffers
        self.temp_file.seek(0)  # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertIn(_words[0], self._weekdays)  # the first part is a date
        self.assertEqual(_words[-1][-1], '\n')  #  the last letter is a newline

    def test_print_date_no_newline(self):
        """Test that we lack a newline at the end"""
        print_date("Test", stream=self.temp_file, newline=False)
        self.temp_file.flush()  # flush buffers
        self.temp_file.seek(0)  # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertNotEqual(_words[-1][-1], '\n')

    def test_print_date_no_date(self):
        """Test that we lack a date at the beginning"""
        print_date("Test", stream=self.temp_file, incl_date=False)
        self.temp_file.flush()  # flush buffers
        self.temp_file.seek(0)  # rewind the files
        data = self.temp_file.readlines()[0]
        _words = data.split(' ')
        self.assertNotIn(_words[0], self._weekdays)  # the first part is a date


class TestParser_prep_binmap(unittest.TestCase):
    def test_default(self):
        """Test default params for prep binmap"""
        args, _ = parse_args(shlex.split('prep binmap file.map'))
        self.assertEqual(args.prep_subcommand, 'binmap')
        self.assertEqual(args.from_file, 'file.map')
        self.assertEqual(args.mask_value, 1)
        self.assertEqual(args.output, 'file_prep.map')
        self.assertEqual(args.contour_level, 0)
        self.assertFalse(args.negate)
        self.assertEqual(args.bytes_per_voxel, 1)
        self.assertEqual(args.infix, 'prep')
        self.assertFalse(args.verbose)

    def test_mask(self):
        """Test setting mask value"""
        mask_value = _random_integer()
        args, _ = parse_args(shlex.split('prep binmap -m {} file.map'.format(mask_value)))
        self.assertEqual(args.mask_value, mask_value)

    def test_output(self):
        """Test that we can set the output"""
        args, _ = parse_args(shlex.split('prep binmap -o my_file.map file.map'))
        self.assertEqual(args.output, 'my_file.map')

    def test_contour_level(self):
        """Test that we can set the contour level"""
        contour_level = _random_float()
        args, _ = parse_args(shlex.split('prep binmap -c {} file.map'.format(contour_level)))
        self.assertEqual(round(args.contour_level, 8), round(contour_level, 8))

    def test_negate(self):
        """Test that we can set negate"""
        args, _ = parse_args(shlex.split('prep binmap --negate file.map'))
        self.assertTrue(args.negate)

    def test_bytes_per_voxel(self):
        """Test that we can set bytes per voxel"""
        bytes_per_voxel = random.choice([1, 2, 4, 8, 16])
        args, _ = parse_args(shlex.split('prep binmap -B {} file.map'.format(bytes_per_voxel)))
        self.assertEqual(args.bytes_per_voxel, bytes_per_voxel)

    def test_infix(self):
        """Test setting infix"""
        args, _ = parse_args(shlex.split('prep binmap --infix something file.map'))
        self.assertEqual(args.infix, 'something')
        self.assertEqual(args.output, 'file_something.map')

    def test_blank_infix(self):
        """Test that a blank infix fails"""
        args, _ = parse_args(shlex.split("prep binmap --infix '' file.map"))
        self.assertIsNone(args)


class TestParser_prep_rescale(unittest.TestCase):
    def test_default(self):
        """Test default param for prep rescale"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        args, _ = parse_args(shlex.split('prep rescale --lengths {lengths} --indices {indices} file.stl'.format(
            lengths=' '.join(map(str, lengths)),
            indices=' '.join(map(str, indices)),
        )))
        self.assertEqual(args.prep_subcommand, 'rescale')
        self.assertEqual(args.from_file, 'file.stl')
        self.assertEqual(args.output, 'file_rescaled.stl')
        self.assertEqual(args.infix, 'rescaled')
        # zip values -> compare using isclose() -> a list of booleans
        l = map(lambda x: isclose(x[0], x[1]), zip(args.lengths, lengths))  # lengths
        i = map(lambda x: isclose(x[0], x[1]), zip(args.indices, indices))  # indices
        # now test that all values in the comparison lists are True using all()
        self.assertTrue(all(l))
        self.assertTrue(all(i))

    def test_origin(self):
        """Test with setting the origin"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(
            shlex.split('prep rescale --lengths {lengths} --indices {indices} --origin {origin} file.stl'.format(
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            )))
        self.assertEqual(args.from_file, 'file.stl')
        # zip values -> compare using isclose() -> a list of booleans
        l = map(lambda x: isclose(x[0], x[1]), zip(args.lengths, lengths))  # lengths
        i = map(lambda x: isclose(x[0], x[1]), zip(args.indices, indices))  # indices
        o = map(lambda x: isclose(x[0], x[1]), zip(args.origin, origin))  # origin
        # now test that all values in the comparison lists are True using all()
        self.assertTrue(all(l))
        self.assertTrue(all(i))
        self.assertTrue(all(o))

    def test_non_stl(self):
        """Test that it fails for non-STL files"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(
            shlex.split('prep rescale --lengths {lengths} --indices {indices} --origin {origin} file.abc'.format(
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            )))
        self.assertIsNone(args)

    def test_output(self):
        """Test that we can set the output"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(
            shlex.split(
                'prep rescale --lengths {lengths} --indices {indices} --origin {origin} -o my_file.stl file.stl'.format(
                    lengths=' '.join(map(str, lengths)),
                    indices=' '.join(map(str, indices)),
                    origin=' '.join(map(str, origin)),
                )))
        self.assertEqual(args.output, 'my_file.stl')

    def test_infix(self):
        """Test setting infix"""
        lengths = _random_floats(count=3, multiplier=1000)
        indices = _random_integers(count=3, start=100, stop=1000)
        origin = _random_floats(count=3, multiplier=10)
        args, _ = parse_args(
            shlex.split(
                'prep rescale --lengths {lengths} --indices {indices} --origin {origin} --infix something file.stl'.format(
                    lengths=' '.join(map(str, lengths)),
                    indices=' '.join(map(str, indices)),
                    origin=' '.join(map(str, origin)),
                )))
        self.assertEqual(args.infix, 'something')
        self.assertEqual(args.output, 'file_something.stl')


class TestParser_convert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("convert tests...", file=sys.stderr)
        cls.test_data_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod')
        cls.test_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.sff')
        cls.test_hff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.hff')
        cls.empty_maps = glob.glob(os.path.join(TEST_DATA_PATH, 'segmentations', 'empty*.map'))
        cls.empty_stls = glob.glob(os.path.join(TEST_DATA_PATH, 'segmentations', 'empty*.stl'))
        cls.empty_segs = glob.glob(os.path.join(TEST_DATA_PATH, 'segmentations', 'empty*.seg'))

    @classmethod
    def tearDownClass(cls):
        print("", file=sys.stderr)

    def test_default(self):
        """Test convert parser"""
        args, _ = parse_args(shlex.split('convert {}'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.subcommand, 'convert')
        self.assertEqual(args.from_file, self.test_data_file)
        self.assertIsNone(args.config_path)
        self.assertFalse(args.top_level_only)
        self.assertEqual(args.details, "")
        self.assertEqual(args.output, os.path.join(os.path.dirname(self.test_data_file), 'test_data.sff'))
        self.assertEqual(args.primary_descriptor, None)
        self.assertFalse(args.verbose)
        self.assertFalse(args.multi_file)

    def test_config_path(self):
        """Test setting of arg config_path"""
        config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'sff.conf')
        args, _ = parse_args(shlex.split('convert --config-path {} {}'.format(config_fn, self.test_data_file)))
        self.assertEqual(args.config_path, config_fn)

    def test_details(self):
        """Test convert parser with details"""
        args, _ = parse_args(shlex.split('convert -d "Some details" {}'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.details, 'Some details')

    def test_output_sff(self):
        """Test convert parser to .sff"""
        args, _ = parse_args(shlex.split('convert {} -o file.sff'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.output, 'file.sff')

    def test_output_hff(self):
        """Test convert parser to .hff"""
        args, _ = parse_args(shlex.split('convert {} -o file.hff'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.output, 'file.hff')

    def test_output_json(self):
        """Test convert parser to .json"""
        args, _ = parse_args(shlex.split('convert {} -o file.json'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.output, 'file.json')

    def test_hff_default_output_sff(self):
        """Test that converting an .hff with no args gives .sff"""
        args, _ = parse_args(shlex.split('convert {}'.format(self.test_hff_file)))
        self.assertEqual(args.output, self.test_sff_file)

    def test_sff_default_output_hff(self):
        """Test that converting a .sff with no args gives .hff"""
        args, _ = parse_args(shlex.split('convert {}'.format(self.test_sff_file)))
        self.assertEqual(args.output, self.test_hff_file)

    def test_primary_descriptor(self):
        """Test convert parser with primary_descriptor"""
        args, _ = parse_args(shlex.split('convert -R threeDVolume {}'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.primary_descriptor, 'threeDVolume')

    def test_wrong_primary_descriptor_fails(self):
        """Test that we have a check on primary descriptor values"""
        # assertions
        with self.assertRaises(ValueError):
            parse_args(shlex.split('convert -R something {}'.format(self.test_data_file)))

    def test_verbose(self):
        """Test convert parser with verbose"""
        args, _ = parse_args(shlex.split('convert -v {}'.format(self.test_data_file)))
        # assertions
        self.assertTrue(args.verbose)

    def test_multifile_map(self):
        """Test that multi-file works for CCP4 masks"""
        args, _ = utils.parse_and_split('convert -v -m {}'.format(' '.join(self.empty_maps)))
        # assertions
        self.assertTrue(args.multi_file)
        self.assertItemsEqual(args.from_file, self.empty_maps)

    def test_multifile_stl(self):
        """Test that multi-file works for STLs"""
        args, _ = utils.parse_and_split('convert -v -m {}'.format(' '.join(self.empty_stls)))
        # assertions
        self.assertTrue(args.multi_file)
        self.assertItemsEqual(args.from_file, self.empty_stls)

    def test_multifile_map_fail1(self):
        """Test that excluding -m issues a warning for CCP4"""
        args, _ = parse_args(shlex.split('convert -v {}'.format(' '.join(self.empty_maps))))
        # assertions
        self.assertIsNone(args)

    def test_multifile_stl_fail2(self):
        """Test that excluding -m issues a warning for STL"""
        args, _ = parse_args(shlex.split('convert -v {}'.format(' '.join(self.empty_stls))))
        # assertions
        self.assertIsNone(args)

    def test_multifile_xxx_fail3(self):
        """Test that other file format fails for multifile e.g. Segger (.seg)"""
        args, _ = parse_args(shlex.split('convert -v {}'.format(' '.join(self.empty_segs))))
        # assertions
        self.assertIsNone(args)

    def test_multifile_xxx_fail4(self):
        """Test that other file format fails even with -m e.g. Segger (.seg)"""
        args, _ = parse_args(shlex.split('convert -v -m {}'.format(' '.join(self.empty_segs))))
        # assertions
        self.assertIsNone(args)


#     def test_exclude_unannotated_regions(self):
#         """Test that we set the exclude unannotated regions flag"""
#         args, _ = parse_args(shlex.split('convert -x {}'.format(self.test_data_file)))
#         # assertions
#         self.assertTrue(args.exclude_unannotated_regions)


class TestParser_view(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        print("view tests...", file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        print("", file=sys.stderr)

    def test_default(self):
        """Test view parser"""
        args, _ = parse_args(shlex.split('view file.sff'))

        self.assertEqual(args.from_file, 'file.sff')
        self.assertFalse(args.version)
        self.assertIsNone(args.config_path)
        self.assertFalse(args.show_chunks)

    def test_version(self):
        """Test view version"""
        args, _ = parse_args(shlex.split('view -V file.sff'))

        self.assertTrue(args.version)

    def test_config_path(self):
        """Test setting of arg config_path"""
        config_fn = os.path.join(TEST_DATA_PATH, 'configs', 'sff.conf')
        args, _ = parse_args(shlex.split('view --config-path {} file.sff'.format(config_fn)))
        self.assertEqual(args.config_path, config_fn)

    def test_show_chunks_mod(self):
        """Test that we can view chunks"""
        args, _ = parse_args(shlex.split('view -C file.mod'))
        self.assertTrue(args.show_chunks)

    def test_show_chunks_other_fails(self):
        """Test that show chunks only works for .mod files"""
        args, _ = parse_args(shlex.split('view -C file.sff'))
        self.assertIsNone(args)


class TestParser_notes_ro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        print("notes ro tests...", file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        print("", file=sys.stderr)

    # =========================================================================
    # find
    # =========================================================================
    def test_search_default(self):
        """Test default find parameters"""
        args, _ = parse_args(shlex.split("notes search 'mitochondria' --config-path {}".format(self.config_fn)))
        self.assertEqual(args.notes_subcommand, 'search')
        self.assertEqual(args.search_term, 'mitochondria')
        self.assertEqual(args.rows, 10)
        self.assertEqual(args.start, 1)
        self.assertIsNone(args.ontology)
        self.assertFalse(args.exact)
        self.assertFalse(args.obsoletes)
        self.assertFalse(args.list_ontologies)
        self.assertFalse(args.short_list_ontologies)
        self.assertEqual(args.config_path, self.config_fn)
        self.assertEqual(args.resource, 'ols')

    def test_search_options(self):
        """Test setting of:
            - number of rows
            - search start
            - ontology
            - exact matches
            - include obsolete entries
            - list of ontologies
            - short list of ontologies
        """
        rows = _random_integer()
        start = _random_integer()
        args, _ = parse_args(shlex.split(
            "notes search -r {} -s {} -O fma -x -o -L -l 'mitochondria' --config-path {}".format(rows, start,
                                                                                                 self.config_fn)))
        self.assertEqual(args.rows, rows)
        self.assertEqual(args.start, start)
        self.assertEqual(args.ontology, 'fma')
        self.assertTrue(args.exact)
        self.assertTrue(args.obsoletes)
        self.assertTrue(args.list_ontologies)
        self.assertTrue(args.short_list_ontologies)
        self.assertEqual(args.search_term, "mitochondria")

    def test_search_invalid_start(self):
        """Test that we catch an invalid start"""
        start = -_random_integer()
        with self.assertRaises(ValueError):
            parse_args(shlex.split("notes search -s {} 'mitochondria' --config-path {}".format(start, self.config_fn)))

    def test_search_invalid_rows(self):
        """Test that we catch an invalid rows"""
        rows = -_random_integer()
        with self.assertRaises(ValueError):
            parse_args(shlex.split("notes search -r {} 'mitochondria' --config-path {}".format(rows, self.config_fn)))

    def test_search_resource_options(self):
        """Test various values of -R/--resource"""
        resources = RESOURCE_LIST.keys()
        for R in resources:
            args, _ = parse_args(
                shlex.split('notes search "term" --resource {} --config-path {}'.format(R, self.config_fn)))
            self.assertEqual(args.resource, R)

    # =========================================================================
    # view
    # =========================================================================
    def test_list_default(self):
        """Test that we can list notes from an SFF file"""
        args, _ = parse_args(shlex.split('notes list file.sff --config-path {}'.format(self.config_fn)))
        #  assertion
        self.assertEqual(args.notes_subcommand, 'list')
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertFalse(args.long_format)
        self.assertFalse(args.sort_by_name)
        self.assertFalse(args.reverse)

    def test_list_long(self):
        """Test short list of notes"""
        args, _ = parse_args(shlex.split('notes list -l file.sff --config-path {}'.format(self.config_fn)))
        # assertions
        self.assertTrue(args.long_format)

    def test_list_shortcut(self):
        """Test that shortcut fails with list"""
        args, _ = parse_args(shlex.split('notes list @ --config-path {}'.format(self.config_fn)))
        #  assertions
        self.assertIsNone(args)

    def test_list_sort_by_name(self):
        """Test list segments sorted by description"""
        args, _ = parse_args(shlex.split('notes list -D file.sff --config-path {}'.format(self.config_fn)))
        # assertions
        self.assertTrue(args.sort_by_name)

    def test_list_reverse_sort(self):
        """Test list sort in reverse"""
        args, _ = parse_args(shlex.split('notes list -r file.sff --config-path {}'.format(self.config_fn)))
        # assertions
        self.assertTrue(args.reverse)

    def test_show_default(self):
        """Test show notes"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args, _ = parse_args(shlex.split(
            'notes show -i {},{} file.sff --config-path {}'.format(segment_id0, segment_id1, self.config_fn)))
        #  assertions
        self.assertEqual(args.notes_subcommand, 'show')
        self.assertItemsEqual(args.segment_id, [segment_id0, segment_id1])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertFalse(args.long_format)

    def test_show_short(self):
        """Test short show of notes"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args, _ = parse_args(shlex.split(
            'notes show -l -i {},{} file.sff --config-path {}'.format(segment_id0, segment_id1, self.config_fn)))
        #  assertions
        self.assertTrue(args.long_format)

    def test_show_shortcut(self):
        """Test that shortcut works with show"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args, _ = parse_args(
            shlex.split('notes show -i {},{} @ --config-path {}'.format(segment_id0, segment_id1, self.config_fn)))
        #  assertions
        self.assertIsNone(args)


class TestParser_notes_rw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        print("notes rw tests...", file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        print("", file=sys.stderr)

    def setUp(self):
        unittest.TestCase.setUp(self)
        _, configs = parse_args(shlex.split('config get --all --config-path {}'.format(self.config_fn)))
        self.temp_file = configs['__TEMP_FILE']
        if os.path.exists(self.temp_file):
            raise ValueError("Unable to run with temp file {} present. \
Please either run 'save' or 'trash' before running tests.".format(self.temp_file))

    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            assert not os.path.exists(self.temp_file)
        unittest.TestCase.tearDown(self)

    # ===========================================================================
    # notes: add
    # ===========================================================================
    def test_add_default(self):
        """Test add notes"""
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        args, _ = parse_args(shlex.split(
            'notes add -i {} -D something -n {} -E abc ABC 123  -C xyz,XYZ -M opq,OPQ file.sff --config-path {}'.format(
                segment_id, number_of_instances, self.config_fn)))
        #  assertions
        self.assertEqual(args.notes_subcommand, 'add')
        self.assertItemsEqual(args.segment_id, [segment_id])
        self.assertEqual(args.description, 'something')
        self.assertEqual(args.number_of_instances, number_of_instances)
        self.assertItemsEqual(args.external_ref, [['abc', 'ABC', '123']])
        self.assertItemsEqual(args.complexes, ['xyz', 'XYZ'])
        self.assertItemsEqual(args.macromolecules, ['opq', 'OPQ'])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_add_addendum_missing(self):
        """Test assertion fails if addendum is missing"""
        segment_id = _random_integer()
        args, _ = parse_args(
            shlex.split('notes add -i {} file.sff --config-path {}'.format(segment_id, self.config_fn)))
        self.assertEqual(args, None)

    # ===========================================================================
    # notes: edit
    # ===========================================================================
    def test_edit_default(self):
        """Test edit notes"""
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        external_ref_id = _random_integer()
        complex_id = _random_integer()
        macromolecule_id = _random_integer()
        args, _ = parse_args(shlex.split(
            'notes edit -i {} -D something -n {} -e {} -E abc ABC 123 -c {} -C xyz -m {} -M opq file.sff --config-path {}'.format(
                segment_id, number_of_instances, external_ref_id, complex_id, macromolecule_id,
                self.config_fn,
            )))

        self.assertEqual(args.notes_subcommand, 'edit')
        self.assertItemsEqual(args.segment_id, [segment_id])
        self.assertEqual(args.description, 'something')
        self.assertEqual(args.number_of_instances, number_of_instances)
        self.assertEqual(args.external_ref_id, external_ref_id)
        self.assertItemsEqual(args.external_ref, [['abc', 'ABC', '123']])
        self.assertEqual(args.complex_id, complex_id)
        self.assertItemsEqual(args.complexes, ['xyz'])
        self.assertEqual(args.macromolecule_id, macromolecule_id)
        self.assertItemsEqual(args.macromolecules, ['opq'])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_edit_failure_on_missing_ids(self):
        """Test handling of missing IDs"""
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        external_ref_id = _random_integer()
        complex_id = _random_integer()
        macromolecule_id = _random_integer()
        args, _ = parse_args(shlex.split(
            'notes edit -i {} -D something -n {} -E abc ABC 123 -c {} -C xyz -m {} -M opq file.sff --config-path {}'.format(
                segment_id, number_of_instances, complex_id, macromolecule_id,
                self.config_fn,
            )))

        self.assertIsNone(args)

        args1, _ = parse_args(shlex.split(
            'notes edit -i {} -D something -n {} -e {} -E abc ABC 123 -C xyz -m {} -M opq @  --config-path {}'.format(
                segment_id, number_of_instances, external_ref_id, macromolecule_id,
                self.config_fn,
            )))

        self.assertIsNone(args1)

        args2, _ = parse_args(shlex.split(
            'notes edit -i {} -D something -n {} -e {} -E abc ABC 123 -c {} -C xyz -M opq @  --config-path {}'.format(
                segment_id, number_of_instances, external_ref_id, complex_id,
                self.config_fn,
            )))

        self.assertIsNone(args2)

    # ===========================================================================
    # notes: del
    # ===========================================================================
    def test_del_default(self):
        """Test del notes"""
        segment_id = _random_integer()
        external_ref_id = _random_integer()
        complex_id = _random_integer()
        macromolecule_id = _random_integer()
        args, _ = parse_args(shlex.split('notes del -i {} -D -n -e {} -c {} -m {} file.sff --config-path {}'.format(
            segment_id, external_ref_id, complex_id, macromolecule_id,
            self.config_fn,
        )))

        self.assertEqual(args.notes_subcommand, 'del')
        self.assertItemsEqual(args.segment_id, [segment_id])
        self.assertTrue(args.description)
        self.assertTrue(args.number_of_instances)
        self.assertEqual(args.external_ref_id, external_ref_id)
        self.assertEqual(args.complex_id, complex_id)
        self.assertEqual(args.macromolecule_id, macromolecule_id)
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    # =========================================================================
    # notes: copy
    # =========================================================================
    def test_copy_default(self):
        """Test that we can run copy"""
        source_id = _random_integer(start=1)
        other_id = _random_integer(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=source_id, other_id=other_id, config_fn=self.config_fn, )
        print(cmd, file=sys.stderr)
        args, _ = parse_args(shlex.split(cmd))
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertItemsEqual(args.segment_id, [source_id])
        self.assertItemsEqual(args.to_segment, [other_id])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_to_multiple(self):
        """Test that we can copy from one to multiple"""
        source_id = _random_integer(start=1)
        other_id = _random_integers(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=source_id, other_id=','.join(map(str, other_id)), config_fn=self.config_fn, )
        print(cmd, file=sys.stderr)
        args, _ = parse_args(shlex.split(cmd))
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertItemsEqual(args.segment_id, [source_id])
        self.assertItemsEqual(args.to_segment, other_id)
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_from_multiple(self):
        """Test that we can copy from multiple to one"""
        source_id = _random_integers(start=1)
        other_id = _random_integer(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=','.join(map(str, source_id)), other_id=other_id, config_fn=self.config_fn, )
        print(cmd, file=sys.stderr)
        args, _ = parse_args(shlex.split(cmd))
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertItemsEqual(args.segment_id, source_id)
        self.assertItemsEqual(args.to_segment, [other_id])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_from_multiple_to_multiple(self):
        """Test that we can copy from multiple to multiple"""
        source_id = _random_integers(start=1, stop=100)
        other_id = _random_integers(start=101, stop=200)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=','.join(map(str, source_id)), other_id=','.join(map(str, other_id)), config_fn=self.config_fn, )
        print('source_id: ', source_id, file=sys.stderr)
        args, _ = parse_args(shlex.split(cmd))
        self.assertEqual(args.notes_subcommand, 'copy')
        self.assertItemsEqual(args.segment_id, source_id)
        self.assertItemsEqual(args.to_segment, other_id)
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_copy_check_unique_ids(self):
        """Test that we don't copy ids between the same segment"""
        source_id = _random_integers(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --config-path {config_fn} file.sff '.format(
            source_id=','.join(map(str, source_id)), other_id=','.join(map(str, source_id)), config_fn=self.config_fn, )
        args, _ = parse_args(shlex.split(cmd))
        # with self.assertRaises(ValueError):
        self.assertIsNone(args)

    def test_copy_all(self):
        """Test that we can copy to all others"""
        # all other ids should be correctly generated
        source_id = _random_integer(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-all --config-path {config_fn} file.sff'.format(
            source_id=source_id,
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertTrue(args.to_all)

    def test_copy_to_and_all_exception(self):
        source_id = _random_integer(start=1)
        other_id = _random_integer(start=1)
        cmd = 'notes copy --segment-id {source_id} --to-segment {other_id} --to-all --config-path {config_fn} file.sff'.format(
            source_id=source_id,
            other_id=other_id,
            config_fn=self.config_fn,
        )
        with self.assertRaises(SystemExit):
            args, _ = parse_args(shlex.split(cmd))

    def test_copy_from_global_notes(self):
        """Test copy from global"""
        other_id = _random_integers(start=1)
        cmd = "notes copy --from-global --to-segment {other_id} --config-path {config_fn} file.sff".format(
            other_id=','.join(map(str, other_id)),
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertTrue(args.from_global)
        self.assertFalse(args.to_global)

    def test_copy_to_global_notes(self):
        """Test copy to global"""
        source_id = _random_integer(start=1)
        cmd = "notes copy --segment-id {source_id} --to-global --config-path {config_fn} file.sff".format(
            source_id=source_id,
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertTrue(args.to_global)
        self.assertFalse(args.from_global)

    # =========================================================================
    # notes: clear
    # =========================================================================
    def test_clear_default(self):
        """Test that we can clear notes for a single segment"""
        source_id = _random_integer(start=1)
        cmd = "notes clear --segment-id {source_id} --config-path {config_fn} file.sff".format(
            source_id=source_id,
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertEqual(args.notes_subcommand, 'clear')
        self.assertEqual(args.segment_id, [source_id])
        self.assertFalse(args.from_all_segments)

    def test_clear_multiple(self):
        """Test that we can clear many but not all"""
        source_id = _random_integers(start=1)
        cmd = "notes clear --segment-id {source_id} --config-path {config_fn} file.sff".format(
            source_id=','.join(map(str, source_id)),
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertEqual(args.segment_id, source_id)

    def test_clear_all_except_global(self):
        """Test that we can clear all except global"""
        cmd = "notes clear --from-all-segments --config-path {config_fn} file.sff".format(
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertTrue(args.from_all_segments)

    def test_clear_global_only(self):
        """Test that we can clear global only"""
        cmd = "notes clear --from-global --config-path {config_fn} file.sff".format(
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertTrue(args.from_global)

    def test_clear_all(self):
        """Test that we can clear all notes"""
        cmd = "notes clear --all --config-path {config_fn} file.sff".format(
            config_fn=self.config_fn,
        )
        args, _ = parse_args(shlex.split(cmd))
        self.assertTrue(args.all)
        self.assertTrue(args.from_global)
        self.assertTrue(args.from_all_segments)

    # =========================================================================
    # notes: save
    # =========================================================================
    def test_save(self):
        """Test save edits"""
        segment_id = _random_integer()
        args, _ = parse_args(
            shlex.split("notes edit -i {} -D something file.sff --config-path {}".format(segment_id, self.config_fn)))
        self.assertEqual(args.sff_file, 'file.sff')
        #  can only save to an existing file
        save_fn = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.sff')
        args1, _ = parse_args(shlex.split("notes save {} --config-path {}".format(save_fn, self.config_fn)))
        self.assertEqual(args1.notes_subcommand, 'save')
        self.assertEqual(args1.sff_file, save_fn)
        self.assertEqual(args.config_path, self.config_fn)

    # ===========================================================================
    # notes: trash
    # ===========================================================================
    def test_trash(self):
        """Test trash notes"""
        segment_id = _random_integer()
        args, _ = parse_args(
            shlex.split("notes edit -i {} -D something file.sff --config-path {}".format(segment_id, self.config_fn)))
        self.assertEqual(args.sff_file, 'file.sff')
        args1, _ = parse_args(shlex.split("notes trash @ --config-path {}".format(self.config_fn)))
        self.assertEqual(args1.notes_subcommand, 'trash')
        self.assertEqual(args.config_path, self.config_fn)

    # ===========================================================================
    # notes: merge vanilla
    # ===========================================================================
    def test_merge(self):
        """Test merge notes"""
        args, _ = parse_args(shlex.split(
            "notes merge --source file.json file.hff --output file.sff --config-path {}".format(self.config_fn)))
        self.assertEqual(args.source, 'file.json')
        self.assertEqual(args.other, 'file.hff')
        self.assertEqual(args.output, 'file.sff')
        self.assertEqual(args.config_path, self.config_fn)

    def test_merge_output_implied(self):
        """Test with output implied i.e. no --output arg"""
        args, _ = parse_args(
            shlex.split("notes merge --source file.json file.hff --config-path {}".format(self.config_fn)))
        self.assertEqual(args.source, 'file.json')
        self.assertEqual(args.other, 'file.hff')
        self.assertEqual(args.output, 'file.hff')
        self.assertEqual(args.config_path, self.config_fn)


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("utils tests...", file=sys.stderr)

    def test_get_path_one_level(self):
        """Test that we can get an item at a path one level deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': x, 1: y}
        path = ['a']
        self.assertEqual(utils.get_path(D, path), x)
        path = [1]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_two_level(self):
        """Test that we can get an item at a path two levels deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': x,
            1: y,
        }}
        path = ['a', 'b']
        self.assertEqual(utils.get_path(D, path), x)
        path = ['a', 1]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_three_levels(self):
        """Test that we can get an item at a path three levels deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': {
                'c': x,
            },
            1: {
                2: y,
            }
        }}
        path = ['a', 'b', 'c']
        self.assertEqual(utils.get_path(D, path), x)
        path = ['a', 1, 2]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_four_levels(self):
        """Test that we can get an item at a path four levels deep"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': {
                'c': {
                    'd': x,
                },
                1: {
                    2: y,
                }
            }
        }}
        path = ['a', 'b', 'c', 'd']
        self.assertEqual(utils.get_path(D, path), x)
        path = ['a', 'b', 1, 2]
        self.assertEqual(utils.get_path(D, path), y)

    def test_get_path_keyerror(self):
        """Test that we get a KeyError exception if the path does not exist"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': {
            'b': {
                'c': {
                    'd': x,
                },
                'e': {
                    'f': y,
                }
            }
        }}
        path = ['a', 'b', 'c', 'f']
        with self.assertRaises(KeyError):
            utils.get_path(D, path)

    def test_get_path_nondict_type_error(self):
        """Test that we get an exception when D is not a dict"""
        D = ['some rubbish list']
        path = ['a']
        with self.assertRaises(AssertionError):
            utils.get_path(D, path)

    def test_get_path_unhashable_in_path(self):
        """Test that unhashable in path fails"""
        x = _random_integer()
        y = _random_integer()
        D = {'a': x, 'b': y}
        path = [[5]]
        with self.assertRaises(TypeError):
            utils.get_path(D, path)


class TestPrep(unittest.TestCase):
    def test_binmap_default(self):
        """Test binarise map"""
        test_map_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map')
        args, _ = parse_args(shlex.split("prep binmap -v {}".format(test_map_file)))
        ex_st = bin_map(args, _)
        self.assertEqual(ex_st, os.EX_OK)
        # clean up
        os.remove(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_prep.map'))

    def test_transform_stl_default(self):
        """Test rescale stl"""
        # the original STL file
        test_stl_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.stl')
        # lengths = _random_floats(count=3, multiplier=1000)
        # indices = _random_integers(count=3, start=100, stop=1000)
        # origin = _random_floats(count=3, multiplier=10)
        lengths = (2000, 2000, 2000)
        indices = (1000, 1000, 1000)
        origin = (100, 200, 300)
        args, _ = parse_args(shlex.split(
            "prep rescale --lengths {lengths} --indices {indices} --origin {origin} --verbose {file}".format(
                file=test_stl_file,
                lengths=' '.join(map(str, lengths)),
                indices=' '.join(map(str, indices)),
                origin=' '.join(map(str, origin)),
            )))
        # manual_transform
        lengths = numpy.array(args.lengths, dtype=numpy.float32)
        indices = numpy.array(args.indices, dtype=numpy.int32)
        voxel_size = numpy.divide(lengths, indices)
        origin = numpy.array(args.origin, dtype=numpy.float32)
        transform_manual = numpy.array([
            [voxel_size[0], 0, 0, origin[0]],
            [0, voxel_size[1], 0, origin[1]],
            [0, 0, voxel_size[2], origin[2]],
            [0, 0, 0, 1]
        ], dtype=numpy.float32)
        # transform from function
        transform_f = construct_transformation_matrix(args)
        self.assertTrue(numpy.allclose(transform_manual, transform_f))
        original_mesh = Mesh.from_file(test_stl_file)
        # the upper limit for random ints
        no_verts = original_mesh.v0.shape[0]
        # random vertices
        v0_index = _random_integer(start=0, stop=no_verts)
        v1_index = _random_integer(start=0, stop=no_verts)
        v2_index = _random_integer(start=0, stop=no_verts)
        # rescale the mesh
        rescaled_mesh = transform_stl_mesh(original_mesh, transform_f)
        # make sure the shapes are identical
        self.assertEqual(original_mesh.v0.shape, rescaled_mesh.v0.shape)
        self.assertEqual(original_mesh.v1.shape, rescaled_mesh.v1.shape)
        self.assertEqual(original_mesh.v2.shape, rescaled_mesh.v2.shape)
        # now we pick some vertices at random and compare them
        rescaled_vertex_v0 = numpy.dot(transform_f[0:3, 0:3], original_mesh.v0[v0_index].T).T
        rescaled_vertex_v0 += transform_f[0:3, 3].T
        rescaled_vertex_v1 = numpy.dot(transform_f[0:3, 0:3], original_mesh.v1[v1_index].T).T
        rescaled_vertex_v1 += transform_f[0:3, 3].T
        rescaled_vertex_v2 = numpy.dot(transform_f[0:3, 0:3], original_mesh.v2[v2_index].T).T
        rescaled_vertex_v2 += transform_f[0:3, 3].T
        self.assertTrue(numpy.allclose(rescaled_vertex_v0, rescaled_mesh.v0[v0_index]))
        self.assertTrue(numpy.allclose(rescaled_vertex_v1, rescaled_mesh.v1[v1_index]))
        self.assertTrue(numpy.allclose(rescaled_vertex_v2, rescaled_mesh.v2[v2_index]))
