"""
sfftk.formats modules unit tests
"""
import argparse
import numbers
import os
import sys
from io import StringIO

import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.unittests import Py23FixTestCase

from . import TEST_DATA_PATH, BASE_DIR
# from .. import schema
from ..core.parser import parse_args, cli
from ..formats import am, seg, map, mod, stl, surf, survos, ilastik

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-03-28"
__updated__ = '2018-02-14'


class TestFormats(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestFormats, cls).setUpClass()
        # path to test files
        cls.segmentations_path = os.path.join(TEST_DATA_PATH, 'segmentations')
        # schema version
        cls.schema_version = schema.SFFSegmentation().version

    def read_am(self):
        """Read .am files"""
        if not hasattr(self, 'am_file'):
            self.am_file = os.path.join(self.segmentations_path, 'test_data.am')
            self.am_segmentation = am.AmiraMeshSegmentation(self.am_file)

    def read_ilastik(self):
        """Read ilastik .h5 files"""
        if not hasattr(self, 'ilastik_file'):
            self.ilastik_file = os.path.join(self.segmentations_path, 'test_data_ilastik.h5')
            self.ilastik_segmentation = ilastik.IlastikSegmentation(self.ilastik_file)

    def read_seg(self):
        """Read .seg files"""
        if not hasattr(self, 'seg_file'):
            self.seg_file = os.path.join(self.segmentations_path, 'test_data.seg')
            self.seg_segmentation = seg.SeggerSegmentation(self.seg_file)

    def read_map(self):
        """Read .map/.mrc/.rec files"""
        if not hasattr(self, 'map_file'):
            self.map_file = os.path.join(self.segmentations_path, 'test_data.map')
            self.map_segmentation = map.MapSegmentation([self.map_file])

    def read_single_mask(self):
        """Read .map/.mrc/.rec file"""
        if not hasattr(self, 'mask_file'):
            self.mask_file = os.path.join(self.segmentations_path, 'test_data.map')
            self.mask_segmentation = map.BinaryMaskSegmentation([self.mask_file])

    def read_multiple_mask(self):
        """Read .map/.mrc/.rec files"""
        if not hasattr(self, 'map_multiple_mask'):
            self.multiple_mask_1 = os.path.join(self.segmentations_path, 'test_data_multi0.map')
            self.multiple_mask_2 = os.path.join(self.segmentations_path, 'test_data_multi1.map')
            self.multiple_mask_3 = os.path.join(self.segmentations_path, 'test_data_multi2.map')
            self.multiple_mask_segmentation = map.BinaryMaskSegmentation(
                [self.multiple_mask_1, self.multiple_mask_2, self.multiple_mask_3]
            )

    def read_merged_mask(self):
        """Read a merged mask from several masks with the label tree JSON file in tow"""
        if not hasattr(self, 'merged_mask'):
            self.merged_mask_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'merged_mask.mrc')
            self.merged_mask_labels_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'merged_mask.json')
            self.merged_mask_segmentation = map.MergedMaskSegmentation(
                self.merged_mask_file,
                label_tree=self.merged_mask_labels_file
            )

    def read_map_multi(self):
        """Read .map multi files"""
        if not hasattr(self, 'map_multi0_file'):
            self.map_multi0_file = os.path.join(self.segmentations_path, 'test_data_multi0.map')
            self.map_multi1_file = os.path.join(self.segmentations_path, 'test_data_multi1.map')
            self.map_multi2_file = os.path.join(self.segmentations_path, 'test_data_multi2.map')
            self.map_multi_segmentation = map.MapSegmentation(
                [self.map_multi0_file, self.map_multi1_file, self.map_multi2_file]
            )

    def read_mod(self):
        """Read .mod files"""
        if not hasattr(self, 'mod_file'):
            self.mod_file = os.path.join(self.segmentations_path, 'test_data.mod')
            # self.mod_file = '/Users/pkorir/data/for_debugging/mod/input_file.mod' # -25 multiple
            # self.mod_file = '/Users/pkorir/data/segmentations/mod/test10.mod' # -23
            self.mod_segmentation = mod.IMODSegmentation(self.mod_file)

    def read_stl(self):
        """Read .stl files"""
        if not hasattr(self, 'stl_file'):
            self.stl_file = os.path.join(self.segmentations_path, 'test_data.stl')
            self.stl_segmentation = stl.STLSegmentation([self.stl_file])

    def read_stl_multi(self):
        """Read .stl multi files"""
        if not hasattr(self, 'stl_multi0_file'):
            self.stl_multi0_file = os.path.join(self.segmentations_path, 'test_data_multi0.stl')
            self.stl_multi1_file = os.path.join(self.segmentations_path, 'test_data_multi1.stl')
            self.stl_multi2_file = os.path.join(self.segmentations_path, 'test_data_multi2.stl')
            self.stl_multi_segmentation = stl.STLSegmentation(
                [self.stl_multi0_file, self.stl_multi1_file, self.stl_multi2_file]
            )

    def read_surf(self):
        """Read .surf files"""
        if not hasattr(self, 'surf_file'):
            self.surf_file = os.path.join(self.segmentations_path, 'test_data.surf')
            self.surf_segmentation = surf.AmiraHyperSurfaceSegmentation(self.surf_file)

    def read_survos(self):
        """Read SuRVoS .h5 files"""
        if not hasattr(self, 'survos_file'):
            self.survos_file = os.path.join(self.segmentations_path, 'test_data.h5')
            self.survos_segmentation = survos.SuRVoSSegmentation(self.survos_file)

    # read
    def test_am_read(self):
        """Read an AmiraMesh (.am) segmentation"""
        self.read_am()
        # assertions
        self.assertIsInstance(self.am_segmentation.header, am.AmiraMeshHeader)
        self.assertIsInstance(self.am_segmentation.segments, list)
        # self.assertIsInstance(self.am_segmentation.segments[0], am.AmiraMeshSegment)

    def test_ilastik_read(self):
        """Read an ilastik (.h5) segmentation"""
        self.read_ilastik()
        self.assertIsInstance(self.ilastik_segmentation.header, ilastik.IlastikHeader)
        self.assertIsInstance(list(self.ilastik_segmentation.segments), list)
        self.assertIsInstance(list(self.ilastik_segmentation.segments)[0], ilastik.IlastikSegment)

    def test_seg_read(self):
        """Read a Segger (.seg) segmentation"""
        self.read_seg()
        # assertions
        self.assertIsInstance(self.seg_segmentation.header, seg.SeggerHeader)
        self.assertIsInstance(self.seg_segmentation.segments, list)
        self.assertIsInstance(self.seg_segmentation.segments[0], seg.SeggerSegment)

    def test_map_read(self):
        """Read an EMDB Map mask (.map) segmentation"""
        with self.assertWarns(PendingDeprecationWarning):
            self.read_map()
        # assertions
        self.assertIsInstance(self.map_segmentation.header, map.MapHeader)
        self.assertIsInstance(self.map_segmentation.segments, list)
        self.assertIsInstance(self.map_segmentation.segments[0], map.MapSegment)

    def test_mask_read(self):
        """Test that we can read masks (.map/.mrc/.rec) segmentation"""
        self.read_single_mask()
        # assertions
        self.assertIsInstance(self.mask_segmentation.header, map.MaskHeader)
        self.assertIsInstance(self.mask_segmentation.segments, list)
        self.assertIsInstance(self.mask_segmentation.segments[0], map.BinaryMaskSegment)

    def test_multiple_mask_read(self):
        """Test that we can read multiple masks as a segmentation"""
        self.read_multiple_mask()
        # assertions
        self.assertIsInstance(self.multiple_mask_segmentation.header, map.MaskHeader)
        self.assertIsInstance(self.multiple_mask_segmentation.segments, list)
        self.assertIsInstance(self.multiple_mask_segmentation.segments[0], map.BinaryMaskSegment)

    def test_merged_mask_read(self):
        """Test that we can read multiple masks as a segmentation"""
        self.read_merged_mask()
        # assertions
        self.assertIsInstance(self.merged_mask_segmentation.header, map.MaskHeader)
        self.assertIsInstance(self.merged_mask_segmentation.segments, list)
        self.assertIsInstance(self.merged_mask_segmentation.segments[0], map.MergedMaskSegment)

    def test_mod_read(self):
        """Read an IMOD (.mod) segmentation"""
        self.read_mod()
        # assertions
        self.assertIsInstance(self.mod_segmentation.header, mod.IMODHeader)
        self.assertIsInstance(self.mod_segmentation.segments, list)
        self.assertIsInstance(self.mod_segmentation.segments[0], mod.IMODSegment)

    def test_stl_read(self):
        """Read a Stereo Lithography (.stl) segmentation"""
        self.read_stl()
        # assertions
        self.assertIsInstance(self.stl_segmentation.header, stl.STLHeader)
        self.assertIsInstance(self.stl_segmentation.segments, list)
        self.assertIsInstance(self.stl_segmentation.segments[0], stl.STLSegment)

    def test_surf_read(self):
        """Read a HyperSurface (.surf) segmentation"""
        self.read_surf()
        # assertions
        self.assertIsInstance(self.surf_segmentation.header, surf.AmiraHyperSurfaceHeader)
        self.assertIsInstance(self.surf_segmentation.segments, list)
        self.assertIsInstance(self.surf_segmentation.segments[0], surf.AmiraHyperSurfaceSegment)

    def test_survos_read(self):
        """Read a SuRVoS (.h5) segmentation"""
        self.read_survos()
        segmentation = self.survos_segmentation
        self.assertIsInstance(segmentation, survos.SuRVoSSegmentation)
        self.assertIsInstance(segmentation.segments, list)
        self.assertIsInstance(segmentation.segments[0], survos.SuRVoSSegment)
        self.assertIsInstance(segmentation.segments[0].segment_id, int)

    # convert
    def test_am_convert(self):
        """Convert a segmentation from an AmiraMesh file to an SFFSegmentation object"""
        self.read_am()
        args, configs = parse_args('convert {}'.format(self.am_file), use_shlex=True)
        seg = self.am_segmentation.convert(details=args.details, verbose=True)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'AmiraMesh Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Amira')
        self.assertEqual("Unspecified", seg.software_list[0].version)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        if seg.lattice_list[0].data != '':  # MemoryError will set .data to an emtpy string
            self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_ilastik_convert(self):
        """Convert a segmentation from an AmiraMesh file to an SFFSegmentation object"""
        self.read_ilastik()
        args, configs = parse_args('convert {} --details ilastik --subtype-index 1'.format(self.ilastik_file),
                                   use_shlex=True)
        seg = self.ilastik_segmentation.convert(details=args.details, verbose=True)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual('ilastik Segmentation', seg.name)
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual("ilastik", seg.software_list[0].name)
        self.assertEqual("Unspecified", seg.software_list[0].version)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertEqual('ilastik', seg.details)
        if seg.lattice_list[0].data != '':  # MemoryError will set .data to an emtpy string
            self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_seg_convert(self):
        """Convert a segmentation from a Segger file to an SFFSegmentation object"""
        self.read_seg()
        args, configs = parse_args('convert {}'.format(self.seg_file), use_shlex=True)
        seg = self.seg_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'Segger Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'segger')
        self.assertEqual(seg.software_list[0].version, self.seg_segmentation.header.version)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_map_convert(self):
        """Convert a segmentation from an EMDB Map mask file to an SFFSegmentation object"""
        self.read_map()
        args, configs = parse_args('convert {}'.format(self.map_file), use_shlex=True)
        seg = self.map_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual("Unspecified", seg.software_list[0].name)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_single_mask_convert(self):
        """Convert a single mask from an CCP4/MRC file to an SFFSegmentation object"""
        self.read_single_mask()
        args, configs = parse_args('convert {}'.format(self.mask_file), use_shlex=True)
        seg = self.mask_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual("Unspecified", seg.software_list[0].name)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_multiple_mask_convert(self):
        """Convert multiple binary masks into an SFFSegmentation object"""
        self.read_multiple_mask()
        args, configs = parse_args(
            'convert -m {}'.format(' '.join([self.multiple_mask_1, self.multiple_mask_2, self.multiple_mask_3])),
            use_shlex=True)
        seg = self.multiple_mask_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual("Unspecified", seg.software_list[0].name)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual(len(seg.segment_list), 3)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_merged_mask_convert(self):
        """Convert a merged mask into an SFFSegmentation object"""
        self.read_merged_mask()
        args, configs = cli(f'convert {self.merged_mask_file} --label-tree {self.merged_mask_labels_file}')
        seg = self.merged_mask_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'Merged CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual("Unspecified", seg.software_list[0].name)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual(len(seg.segment_list), 7)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_mask_nonbinary_fail(self):
        """Test that we can detect if a non-binary mask is assumed to be binary"""
        input_ = os.path.join(TEST_DATA_PATH, 'segmentations', 'merged_mask.mrc')
        output = os.path.join(TEST_DATA_PATH, 'test_data.sff')
        config_path = os.path.join(BASE_DIR, 'sff.conf')
        args, configs = cli(f"convert -o {output} {input_} --config-path {config_path}")
        self.assertEqual(65, args)

    def test_mask_nonbinary_ok(self):
        """Test that we are OK to convert a non-binary if the label tree is present"""
        input_ = os.path.join(TEST_DATA_PATH, 'segmentations', 'merged_mask.mrc')
        input_label_tree = os.path.join(TEST_DATA_PATH, 'segmentations', 'merged_mask.json')
        output = os.path.join(TEST_DATA_PATH, 'test_data.sff')
        config_path = os.path.join(BASE_DIR, 'sff.conf')
        args, configs = cli(f"convert -o {output} {input_} --label-tree {input_label_tree} --config-path {config_path}")
        self.assertIsInstance(args, argparse.Namespace)

    def test_map_multi_convert(self):
        """Convert several EMDB Map mask files to a single SFFSegmentation object"""
        self.read_map_multi()
        args, configs = parse_args(
            'convert -m {}'.format(' '.join([self.map_multi0_file, self.map_multi1_file, self.map_multi2_file])),
            use_shlex=True)
        seg = self.map_multi_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'CCP4 mask segmentation')  # might have an extra space at the end
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual("Unspecified", seg.software_list[0].name)
        self.assertEqual(seg.primary_descriptor, 'three_d_volume')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual(len(seg.segment_list), 3)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertGreaterEqual(len(seg.lattice_list), 1)
        self.assertGreater(len(seg.lattice_list[0].data), 1)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertIsNotNone(segment.three_d_volume)
        self.assertIsNotNone(segment.three_d_volume.lattice_id)
        self.assertGreaterEqual(segment.three_d_volume.value, 1)

    def test_mod_convert(self):
        """Convert a segmentation from an IMOD file to an SFFSegmentation object"""
        self.read_mod()
        args, configs = parse_args('convert {} --details "Something interesting"'.format(self.mod_file), use_shlex=True)
        seg = self.mod_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'IMOD-NewModel')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'IMOD')
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transforms[0].id, 0)
        self.assertGreaterEqual(len(seg.transform_list), 1)
        self.assertEqual("Something interesting", seg.details)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_stl_convert(self):
        """Convert a segmentation from an Stereo Lithography file to an SFFSegmentation object"""
        self.read_stl()
        args, configs = parse_args('convert {} --details Nothing'.format(self.stl_file), use_shlex=True)
        seg = self.stl_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'STL Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual("Unspecified", seg.software_list[0].name)
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual("Nothing", seg.details)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_stl_multi_convert(self):
        """Convert several STL files into a single SFFSegmentation object"""
        self.read_stl_multi()
        args, configs = parse_args(
            'convert -m {} --details details'.format(
                ' '.join([self.stl_multi0_file, self.stl_multi1_file, self.stl_multi2_file])),
            use_shlex=True)
        seg = self.stl_multi_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'STL Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual('Unspecified', seg.software_list[0].name)
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual(len(seg.segments), 3)
        self.assertEqual('details', seg.details)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_surf_convert(self):
        """Convert a segmentation from a HyperSurface file to an SFFSegmentation object"""
        self.read_surf()
        args, configs = parse_args('convert {} --details overwhelming'.format(self.surf_file), use_shlex=True)
        seg = self.surf_segmentation.convert(details=args.details)
        # assertions
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, 'Amira HyperSurface Segmentation')
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, 'Amira')
        self.assertEqual(seg.software_list[0].version, self.surf_segmentation.header.version)
        self.assertEqual(seg.primary_descriptor, 'mesh_list')
        self.assertEqual(seg.transform_list[0].id, 0)
        self.assertEqual('overwhelming', seg.details)
        segment = seg.segment_list[0]
        self.assertIsNotNone(segment.biological_annotation)
        self.assertIsNotNone(segment.biological_annotation.name)
        self.assertGreaterEqual(segment.biological_annotation.number_of_instances, 1)
        self.assertIsNotNone(segment.colour)
        self.assertGreaterEqual(len(segment.mesh_list), 1)
        mesh = segment.mesh_list[0]
        self.assertIsNotNone(mesh.vertices)
        self.assertGreater(len(mesh.vertices.data), 1)
        self.assertIsNotNone(mesh.triangles)
        self.assertGreater(len(mesh.triangles.data), 1)
        vertex_ids = set(mesh.triangles.data_array.flatten().tolist())
        self.assertEqual(max(vertex_ids), mesh.vertices.num_vertices - 1)

    def test_survos_convert(self):
        """Convert a segmentation from SuRVoS to SFFSegmentation object"""
        self.read_survos()
        sys.stdin = StringIO('0')
        args, configs = parse_args('convert {} --details survos'.format(self.survos_file), use_shlex=True)
        seg = self.survos_segmentation.convert(details=args.details)
        self.assertIsInstance(seg, schema.SFFSegmentation)
        self.assertEqual(seg.name, "SuRVoS Segmentation")
        self.assertEqual(seg.version, self.schema_version)
        self.assertEqual(seg.software_list[0].name, "SuRVoS")
        self.assertEqual(seg.software_list[0].version, "1.0")
        self.assertEqual(seg.primary_descriptor, "three_d_volume")
        self.assertTrue(len(seg.segment_list) > 0)
        self.assertEqual('survos', seg.details)
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
