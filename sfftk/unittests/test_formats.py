# -*- coding: utf-8 -*-
# test_formats.py
"""
sfftk.formats modules unit tests
"""
from __future__ import division

import numbers
import os

import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.unittests import Py23FixTestCase

from . import TEST_DATA_PATH
# from .. import schema
from ..core.parser import parse_args
from ..formats import am, seg, map, mod, stl, surf, survos

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-03-28"
__updated__ = '2018-02-14'


class TestFormats(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestFormats, cls).setUpClass()
        cls.segmentations_path = os.path.join(TEST_DATA_PATH, 'segmentations')
        # schema version
        cls.schema_version = schema.SFFSegmentation().version
        # files
        cls.am_file = os.path.join(cls.segmentations_path, 'test_data.am')
        cls.seg_file = os.path.join(cls.segmentations_path, 'test_data.seg')
        cls.map_file = os.path.join(cls.segmentations_path, 'test_data.map')
        cls.map_multi0_file = os.path.join(cls.segmentations_path, 'test_data_multi0.map')
        cls.map_multi1_file = os.path.join(cls.segmentations_path, 'test_data_multi1.map')
        cls.map_multi2_file = os.path.join(cls.segmentations_path, 'test_data_multi2.map')
        cls.mod_file = os.path.join(cls.segmentations_path, 'test_data.mod')  # -25
        # cls.mod_file = '/Users/pkorir/data/for_debugging/mod/input_file.mod' # -25 multiple
        # cls.mod_file = '/Users/pkorir/data/segmentations/mod/test10.mod' # -23
        cls.stl_file = os.path.join(cls.segmentations_path, 'test_data.stl')
        cls.stl_multi0_file = os.path.join(cls.segmentations_path, 'test_data_multi0.stl')
        cls.stl_multi1_file = os.path.join(cls.segmentations_path, 'test_data_multi1.stl')
        cls.stl_multi2_file = os.path.join(cls.segmentations_path, 'test_data_multi2.stl')
        cls.surf_file = os.path.join(cls.segmentations_path, 'test_data.surf')
        cls.survos_file = os.path.join(cls.segmentations_path, 'test_data.h5')
        # am
        cls.am_segmentation = am.AmiraMeshSegmentation(cls.am_file)
        # seg
        cls.seg_segmentation = seg.SeggerSegmentation(cls.seg_file)
        # map
        cls.map_segmentation = map.MapSegmentation([cls.map_file])
        # map multi
        cls.map_multi_segmentation = map.MapSegmentation(
            [cls.map_multi0_file, cls.map_multi1_file, cls.map_multi2_file])
        # mod
        cls.mod_segmentation = mod.IMODSegmentation(cls.mod_file)
        # stl
        cls.stl_segmentation = stl.STLSegmentation([cls.stl_file])
        # stl multi
        cls.stl_multi_segmentation = stl.STLSegmentation(
            [cls.stl_multi0_file, cls.stl_multi1_file, cls.stl_multi2_file])
        # surf
        cls.surf_segmentation = surf.AmiraHyperSurfaceSegmentation(cls.surf_file)
        # survos
        cls.survos_segmentation = survos.SuRVoSSegmentation(cls.survos_file)

    # read
    def test_am_read(self):
        """Read an AmiraMesh (.am) segmentation"""
        # assertions
        self.assertIsInstance(self.am_segmentation.header, am.AmiraMeshHeader)
        self.assertIsInstance(self.am_segmentation.segments, list)
        # self.assertIsInstance(self.am_segmentation.segments[0], am.AmiraMeshSegment)

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

    def test_survos_read(self):
        """Read a SuRVoS (.h5) segmentation"""
        segmentation = self.survos_segmentation
        self.assertIsInstance(segmentation, survos.SuRVoSSegmentation)
        self.assertIsInstance(segmentation.segments, list)
        self.assertIsInstance(segmentation.segments[0], survos.SuRVoSSegment)
        self.assertIsInstance(segmentation.segments[0].segment_id, int)

    # convert
    def test_am_convert(self):
        """Convert a segmentation from an AmiraMesh file to an SFFSegmentation object"""
        args, configs = parse_args('convert {}'.format(self.am_file), use_shlex=True)
        sff_segmentation = self.am_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'AmiraMesh Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'Amira')
        self.assertEqual(sff_segmentation.software_list[0].version, self.am_segmentation.header.version)
        # self.assertEqual(sff_segmentation.filePath, os.path.dirname(os.path.abspath(self.am_file)))
        self.assertEqual(sff_segmentation.primary_descriptor, 'three_d_volume')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)

    def test_seg_convert(self):
        """Convert a segmentation from a Segger file to an SFFSegmentation object"""
        args, configs = parse_args('convert {}'.format(self.seg_file), use_shlex=True)
        sff_segmentation = self.seg_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'Segger Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'segger')
        self.assertEqual(sff_segmentation.software_list[0].version, self.seg_segmentation.header.version)
        # self.assertEqual(sff_segmentation.filePath, os.path.dirname(os.path.abspath(self.seg_file)))
        self.assertEqual(sff_segmentation.primary_descriptor, 'three_d_volume')
        self.assertEqual(sff_segmentation.transform_list[0].id, 0)

    def test_map_convert(self):
        """Convert a segmentation from an EMDB Map mask file to an SFFSegmentation object"""
        args, configs = parse_args('convert {}'.format(self.map_file), use_shlex=True)
        sff_segmentation = self.map_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'Undefined')
        self.assertEqual(sff_segmentation.primary_descriptor, 'three_d_volume')
        self.assertEqual(sff_segmentation.transform_list[0].id, 0)

    def test_map_multi_convert(self):
        """Convert several EMDB Map mask files to a single SFFSegmentation object"""
        args, configs = parse_args(
            'convert -m {}'.format(' '.join([self.map_multi0_file, self.map_multi1_file, self.map_multi2_file])),
            use_shlex=True)
        sff_segmentation = self.map_multi_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'Undefined')
        self.assertEqual(sff_segmentation.primary_descriptor, 'three_d_volume')
        self.assertEqual(sff_segmentation.transform_list[0].id, 0)
        self.assertEqual(len(sff_segmentation.segment_list), 3)

    def test_mod_convert(self):
        """Convert a segmentation from an IMOD file to an SFFSegmentation object"""
        args, configs = parse_args('convert {}'.format(self.mod_file), use_shlex=True)
        sff_segmentation = self.mod_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'IMOD-NewModel')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'IMOD')
        self.assertEqual(sff_segmentation.primary_descriptor, 'mesh_list')
        self.assertEqual(sff_segmentation.transforms[0].id, 0)

    def test_stl_convert(self):
        """Convert a segmentation from an Stereo Lithography file to an SFFSegmentation object"""
        args, configs = parse_args('convert {}'.format(self.stl_file), use_shlex=True)
        sff_segmentation = self.stl_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'STL Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'Unknown')
        self.assertEqual(sff_segmentation.primary_descriptor, 'mesh_list')
        self.assertEqual(sff_segmentation.transform_list[0].id, 0)

    def test_stl_multi_convert(self):
        """Convert several STL files into a single SFFSegmentation object"""
        args, configs = parse_args(
            'convert -m {}'.format(' '.join([self.stl_multi0_file, self.stl_multi1_file, self.stl_multi2_file])),
            use_shlex=True)
        sff_segmentation = self.stl_multi_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'STL Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'Unknown')
        self.assertEqual(sff_segmentation.primary_descriptor, 'mesh_list')
        self.assertEqual(sff_segmentation.transform_list[0].id, 0)
        self.assertEqual(len(sff_segmentation.segments), 3)

    def test_surf_convert(self):
        """Convert a segmentation from a HyperSurface file to an SFFSegmentation object"""
        args, configs = parse_args('convert {}'.format(self.surf_file), use_shlex=True)
        sff_segmentation = self.surf_segmentation.convert(args, configs)
        # assertions
        self.assertIsInstance(sff_segmentation, schema.SFFSegmentation)
        self.assertEqual(sff_segmentation.name, 'Amira HyperSurface Segmentation')
        self.assertEqual(sff_segmentation.version, self.schema_version)
        self.assertEqual(sff_segmentation.software_list[0].name, 'Amira')
        self.assertEqual(sff_segmentation.software_list[0].version, self.surf_segmentation.header.version)
        self.assertEqual(sff_segmentation.primary_descriptor, 'mesh_list')
        self.assertEqual(sff_segmentation.transform_list[0].id, 0)

    def test_survos_convert(self):
        """Convert a segmentation from SuRVoS to SFFSegmentation object"""
        args, configs = parse_args('convert {}'.format(self.survos_file), use_shlex=True)
        seg = self.survos_segmentation.convert(args, configs)
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, "SuRVoS Segmentation")
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, "SuRVoS")
        self.assertEqual(seg.software_list[0].version, "1.0")
        self.assertEqual(seg.primary_descriptor, "three_d_volume")
        self.assertTrue(len(seg.segment_list) > 0)
        segment = seg.segment_list.get_by_id(1)
        self.assertEqual(segment.biological_annotation.name, "SuRVoS Segment #1")
        self.assertTrue(0 <= segment.colour.red <= 1)
        self.assertTrue(0 <= segment.colour.green <= 1)
        self.assertTrue(0 <= segment.colour.blue <= 1)
        self.assertTrue(0 <= segment.colour.alpha <= 1)
        lattice = seg.lattice_list.get_by_id(0)
        self.assertEqual(lattice.mode, 'int8')
        self.assertEqual(lattice.endianness, 'little')
        self.assertIsInstance(lattice.size, schema.SFFVolumeStructure)
        self.assertIsInstance(lattice.start, schema.SFFVolumeIndex)
        self.assertTrue(lattice.size.cols > 0)
        self.assertTrue(lattice.size.rows > 0)
        self.assertTrue(lattice.size.sections > 0)
        self.assertIsInstance(lattice.start.cols, numbers.Integral)
        self.assertIsInstance(lattice.start.rows, numbers.Integral)
        self.assertIsInstance(lattice.start.sections, numbers.Integral)
