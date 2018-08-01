# -*- coding: utf-8 -*-
# test_formats.py
"""
sfftk.formats modules unit tests
"""
from __future__ import division

import os
import shlex
import unittest

import __init__ as tests

from .. import schema
from ..core.parser import parse_args
from ..formats import am, seg, map, mod, stl, surf


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-03-28"
__updated__ = '2018-02-14'


class TestFormats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.segmentations_path = os.path.join(tests.TEST_DATA_PATH, 'segmentations')
        # schema version
        cls.schema_version = schema.SFFSegmentation().version
        # files
        cls.am_file = os.path.join(cls.segmentations_path, 'test_data.am')
        cls.seg_file = os.path.join(cls.segmentations_path, 'test_data.seg')
        cls.map_file = os.path.join(cls.segmentations_path, 'test_data.map')
        cls.map_multi0_file = os.path.join(cls.segmentations_path, 'test_data_multi0.map')
        cls.map_multi1_file = os.path.join(cls.segmentations_path, 'test_data_multi1.map')
        cls.map_multi2_file = os.path.join(cls.segmentations_path, 'test_data_multi2.map')
        cls.mod_file = os.path.join(cls.segmentations_path, 'test_data.mod')
        cls.stl_file = os.path.join(cls.segmentations_path, 'test_data.stl')
        cls.stl_multi0_file = os.path.join(cls.segmentations_path, 'test_data_multi0.stl')
        cls.stl_multi1_file = os.path.join(cls.segmentations_path, 'test_data_multi1.stl')
        cls.stl_multi2_file = os.path.join(cls.segmentations_path, 'test_data_multi2.stl')
        cls.surf_file = os.path.join(cls.segmentations_path, 'test_data.surf')
        # am
        cls.am_segmentation = am.AmiraMeshSegmentation(cls.am_file)
        # seg
        cls.seg_segmentation = seg.SeggerSegmentation(cls.seg_file)
        # map
        cls.map_segmentation = map.MapSegmentation([cls.map_file])
        # map multi
        cls.map_multi_segmentation = map.MapSegmentation([cls.map_multi0_file, cls.map_multi1_file, cls.map_multi2_file])
        # mod
        cls.mod_segmentation = mod.IMODSegmentation(cls.mod_file)
        # stl
        cls.stl_segmentation = stl.STLSegmentation([cls.stl_file])
        # stl multi
        cls.stl_multi_segmentation = stl.STLSegmentation([cls.stl_multi0_file, cls.stl_multi1_file, cls.stl_multi2_file])
        # surf
        cls.surf_segmentation = surf.AmiraHyperSurfaceSegmentation(cls.surf_file)

    # read
    def test_am_read(self):
        """Read an AmiraMesh (.am) segmentation"""
        # assertions
        self.assertIsInstance(self.am_segmentation.header, am.AmiraMeshHeader)
        self.assertIsInstance(self.am_segmentation.segments, list)
        self.assertIsInstance(self.am_segmentation.segments[0], am.AmiraMeshSegment)

    def test_seg_read(self):
        """Read a Segger (.seg) segmentation"""
        # assertions
        self.assertIsInstance(self.seg_segmentation.header, seg.SeggerHeader)
        self.assertIsInstance(self.seg_segmentation.segments, list)
        self.assertIsInstance(self.seg_segmentation.segments[0], seg.SeggerSegment)

    def test_map_read(self):
        """Read an EMDB Map mask (.map) segmentation"""
        # assertions
        self.assertIsInstance(self.map_segmentation.header, map.MapHeader)
        self.assertIsInstance(self.map_segmentation.segments, list)
        self.assertIsInstance(self.map_segmentation.segments[0], map.MapSegment)

    def test_mod_read(self):
        """Read an IMOD (.mod) segmentation"""
        # assertions
        self.assertIsInstance(self.mod_segmentation.header, mod.IMODHeader)
        self.assertIsInstance(self.mod_segmentation.segments, list)
        self.assertIsInstance(self.mod_segmentation.segments[0], mod.IMODSegment)

    def test_stl_read(self):
        """Read a Stereo Lithography (.stl) segmentation"""
        # assertions
        self.assertIsInstance(self.stl_segmentation.header, stl.STLHeader)
        self.assertIsInstance(self.stl_segmentation.segments, list)
        self.assertIsInstance(self.stl_segmentation.segments[0], stl.STLSegment)

    def test_surf_read(self):
        """Read a HyperSurface (.surf) segmentation"""
        # assertions
        self.assertIsInstance(self.surf_segmentation.header, surf.AmiraHyperSurfaceHeader)
        self.assertIsInstance(self.surf_segmentation.segments, list)
        self.assertIsInstance(self.surf_segmentation.segments[0], surf.AmiraHyperSurfaceSegment)

    # convert
    def test_am_convert(self):
        """Convert a segmentation from an AmiraMesh file to an SFFSegmentation object"""
        args, configs = parse_args(shlex.split('convert {}'.format(self.am_file)))
        sff_segmentation = self.am_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'AmiraMesh Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'Amira')
        self.assertEqual(sff_segmentation.software.version, self.am_segmentation.header.designation.version)
        # self.assertEqual(sff_segmentation.filePath, os.path.dirname(os.path.abspath(self.am_file)))
        self.assertEqual(sff_segmentation.primaryDescriptor, 'threeDVolume')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)

    def test_seg_convert(self):
        """Convert a segmentation from a Segger file to an SFFSegmentation object"""
        args, configs = parse_args(shlex.split('convert {}'.format(self.mod_file)))
        sff_segmentation = self.seg_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'Segger Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'segger')
        self.assertEqual(sff_segmentation.software.version, self.seg_segmentation.header.version)
        # self.assertEqual(sff_segmentation.filePath, os.path.dirname(os.path.abspath(self.seg_file)))
        self.assertEqual(sff_segmentation.primaryDescriptor, 'threeDVolume')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)

    def test_map_convert(self):
        """Convert a segmentation from an EMDB Map mask file to an SFFSegmentation object"""
        args, configs = parse_args(shlex.split('convert {}'.format(self.map_file)))
        sff_segmentation = self.map_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'Undefined')
        self.assertEqual(sff_segmentation.primaryDescriptor, 'threeDVolume')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)

    def test_map_multi_convert(self):
        """Convert several EMDB Map mask files to a single SFFSegmentation object"""
        args, configs = parse_args(shlex.split(
            'convert -m {}'.format(' '.join([self.map_multi0_file, self.map_multi1_file, self.map_multi2_file]))
        ))
        sff_segmentation = self.map_multi_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'Undefined')
        self.assertEqual(sff_segmentation.primaryDescriptor, 'threeDVolume')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)
        self.assertEqual(len(sff_segmentation.segments), 3)

    def test_mod_convert(self):
        """Convert a segmentation from an IMOD file to an SFFSegmentation object"""
        args, configs = parse_args(shlex.split('convert {}'.format(self.mod_file)))
        sff_segmentation = self.mod_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'IMOD-NewModel')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'IMOD')
        # self.assertEqual(sff_segmentation.filePath, os.path.abspath(self.mod_file))
        self.assertEqual(sff_segmentation.primaryDescriptor, 'meshList')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)

    def test_stl_convert(self):
        """Convert a segmentation from an Stereo Lithography file to an SFFSegmentation object"""
        args, configs = parse_args(shlex.split('convert {}'.format(self.stl_file)))
        sff_segmentation = self.stl_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'STL Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'Unknown')
        self.assertEqual(sff_segmentation.primaryDescriptor, 'meshList')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)

    def test_stl_multi_convert(self):
        """Convert several STL files into a single SFFSegmentation object"""
        args, configs = parse_args(shlex.split(
            'convert -m {}'.format(' '.join([self.stl_multi0_file, self.stl_multi1_file, self.stl_multi2_file]))
        ))
        sff_segmentation = self.stl_multi_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'STL Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'Unknown')
        self.assertEqual(sff_segmentation.primaryDescriptor, 'meshList')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)
        self.assertEqual(len(sff_segmentation.segments), 3)


    def test_surf_convert(self):
        """Convert a segmentation from a HyperSurface file to an SFFSegmentation object"""
        args, configs = parse_args(shlex.split('convert {}'.format(self.surf_file)))
        sff_segmentation = self.surf_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'Amira HyperSurface Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software.name, 'Amira')
        self.assertEqual(sff_segmentation.software.version, self.surf_segmentation.header.designation.version)
        # self.assertEqual(sff_segmentation.filePath, os.path.abspath(self.surf_file))
        self.assertEqual(sff_segmentation.primaryDescriptor, 'meshList')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)


