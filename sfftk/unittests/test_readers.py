"""
sfftk.unittests.test_readers

This testing module should have no side-effects because it only reads.
"""
import glob
import os
import re
import unittest
from math import cos, sin, radians

import ahds
import numpy
import random_words
from sfftkrw.core import _dict_iter_values, _str
from sfftkrw.unittests import Py23FixTestCase

from . import TEST_DATA_PATH
from ..readers import (
    amreader, mapreader, modreader, segreader, stlreader, surfreader, survosreader, ilastikreader, starreader
)

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-05-15"
__updated__ = '2018-02-14'

rw = random_words.RandomWords()


# readers
class TestReadersAmReader(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.am_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.am')
        cls.header, cls.segments_by_stream = amreader.get_data(cls.am_file)

    def test_get_data(self):
        """Test the main entry point: get_data(...)"""
        self.assertIsInstance(self.header, ahds.header.AmiraHeader)
        self.assertIsInstance(self.segments_by_stream.data, numpy.ndarray)
        self.assertGreaterEqual(self.header.data_stream_count, 1)

    def test_first_line_amiramesh(self):
        """test that it's declared as an AmiraMesh file"""
        self.assertEqual(self.header.filetype, 'AmiraMesh')

    def test_first_line_binary_little_endian(self):
        """test that it is formatted as BINARY-LITTLE-ENDIAN"""
        self.assertEqual(self.header.format, 'BINARY')

    def test_first_line_version(self):
        """test that it is version 2.1"""
        self.assertEqual(self.header.version, '2.1')

    def test_lattice_present(self):
        """test Lattice definition exists in definitions"""
        self.assertTrue('Lattice' in self.header.attrs())

    def test_materials_present(self):
        """test Materials exist in parameters"""
        self.assertTrue(hasattr(self.header.Parameters, 'Materials'))

    def test_read_hxsurface(self):
        """Test handling of AmiraMesh hxsurface files"""
        am_hxsurface_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_hxsurface.am')
        header, segments_by_stream = amreader.get_data(am_hxsurface_file)
        self.assertIsInstance(header, ahds.header.AmiraHeader)
        self.assertIsNone(segments_by_stream)


class TestReadersIlastikReader(Py23FixTestCase):
    def setUp(self):
        super().setUp()
        self.ilastik_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_ilastik.h5')

    def test_get_data(self):
        """Test the get_data() function"""
        ilastik_obj = ilastikreader.get_data(self.ilastik_file)
        self.assertIsInstance(ilastik_obj, ilastikreader.IlastikSegmentation)
        self.assertTrue(len(ilastik_obj.segment_ids) > 0)
        self.assertEqual(ilastik_obj.data.dtype, int)
        self.assertTrue(ilastik_obj.num_voxels > 0)
        self.assertTrue(ilastik_obj.dtype, numpy.dtype)
        self.assertTrue(_str(ilastik_obj.dtype), _str)
        self.assertTrue(len(ilastik_obj.shape), 3)
        self.assertIsInstance(ilastik_obj.shape, tuple)
        self.assertTrue(ilastik_obj.num_images > 0)
        self.assertEqual(ilastik_obj.filename, self.ilastik_file)
        self.assertTrue(len(ilastik_obj.segment_ids) > 0)
        self.assertTrue(ilastik_obj.segment_count > 0)


class TestReadersMapReader(Py23FixTestCase):
    def setUp(self):
        super().setUp()
        self.map_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map')

    def test_get_data(self):
        """Test the main entry point: get_data(...)"""
        map_ = mapreader.get_data(self.map_file)
        self.assertIsInstance(map_, mapreader.Map)
        self.assertGreater(map_._nc, 0)
        self.assertGreater(map_._nr, 0)
        self.assertGreater(map_._ns, 0)
        self.assertIn(map_._mode, range(5))
        self.assertIsInstance(map_._ncstart, int)
        self.assertIsInstance(map_._nrstart, int)
        self.assertIsInstance(map_._nsstart, int)
        self.assertGreater(map_._nx, 0)
        self.assertGreater(map_._ny, 0)
        self.assertGreater(map_._nz, 0)
        self.assertGreater(map_._x_length, 0)
        self.assertGreater(map_._y_length, 0)
        self.assertGreater(map_._z_length, 0)
        self.assertTrue(0 < map_._alpha < 180)
        self.assertTrue(0 < map_._beta < 180)
        self.assertTrue(0 < map_._gamma < 180)
        self.assertIn(map_._mapc, range(1, 4))
        self.assertIn(map_._mapr, range(1, 4))
        self.assertIn(map_._maps, range(1, 4))
        self.assertIsInstance(map_._amin, float)
        self.assertIsInstance(map_._amax, float)
        self.assertIsInstance(map_._amean, float)
        self.assertIn(map_._ispg, range(1, 231))
        self.assertTrue(map_._nsymbt % 80 == 0)
        self.assertIn(map_._lskflg, range(2))
        self.assertIsInstance(map_._s11, float)
        self.assertIsInstance(map_._s12, float)
        self.assertIsInstance(map_._s13, float)
        self.assertIsInstance(map_._s21, float)
        self.assertIsInstance(map_._s22, float)
        self.assertIsInstance(map_._s23, float)
        self.assertIsInstance(map_._s31, float)
        self.assertIsInstance(map_._s32, float)
        self.assertIsInstance(map_._s33, float)
        self.assertIsInstance(map_._t1, float)
        self.assertIsInstance(map_._t2, float)
        self.assertIsInstance(map_._t3, float)
        self.assertEqual(map_._map, 'MAP ')
        self.assertIsInstance(map_._machst, _str)
        self.assertGreater(map_._rms, 0)
        self.assertGreater(map_._nlabl, 0)
        ijk_to_xyz_transform = map_.ijk_to_xyz_transform
        skew_matrix = map_.skew_matrix
        skew_translation = map_.skew_translation
        self.assertIsInstance(ijk_to_xyz_transform, numpy.ndarray)
        # transforms
        self.assertEqual(numpy.prod(ijk_to_xyz_transform.shape), 12)
        # check the transformation matrix is non-zero on the diagonal
        self.assertTrue(ijk_to_xyz_transform[0, 0] * ijk_to_xyz_transform[1, 1] * ijk_to_xyz_transform[2, 2] != 0)
        self.assertEqual(numpy.prod(skew_matrix.shape), 9)
        self.assertEqual(numpy.prod(skew_translation.shape), 3)
        self.assertEqual(map_.ijk_to_xyz_transform_data, " ".join(map(repr, ijk_to_xyz_transform.flatten().tolist())))
        self.assertEqual(map_.skew_matrix_data, " ".join(map(repr, skew_matrix.flatten().tolist())))
        self.assertEqual(map_.skew_translation_data, " ".join(map(repr, skew_translation.flatten().tolist())))

    def test_write(self):
        """Test write map file"""
        map_to_write = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_write_map.map')
        written_maps = glob.glob(map_to_write)
        self.assertEqual(len(written_maps), 0)
        with open(map_to_write, 'wb') as f:
            map_ = mapreader.get_data(self.map_file)
            map_.write(f)
        written_maps = glob.glob(map_to_write)
        self.assertEqual(len(written_maps), 1)
        for m in written_maps:
            os.remove(m)

    def test_invert(self):
        """Test invert map intensities"""
        map_ = mapreader.get_data(self.map_file, inverted=False)
        self.assertFalse(map_._inverted)
        map_.invert()
        self.assertTrue(map_._inverted)
        map_ = mapreader.get_data(self.map_file, inverted=True)
        self.assertTrue(map_._inverted)
        # check the inversion is complete and that we add a new label
        with open('rm.map', 'wb') as f:
            map_.write(f)
        map__ = mapreader.get_data('rm.map')
        self.assertEqual(map__._nlabl, 2)
        os.remove('rm.map')

    def test_fix_mask(self):
        """Test fix mask for fixable mask"""
        fixable_mask = mapreader.Map(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_fixable_mask.map'))
        self.assertFalse(fixable_mask.is_mask)
        fixable_mask.fix_mask()
        self.assertTrue(fixable_mask.is_mask)

    def test_unfixable_mask(self):
        """Test exception for unfixable mask"""
        unfixable_mask = mapreader.Map(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_unfixable_mask.map'))
        self.assertFalse(unfixable_mask.is_mask)
        with self.assertRaises(ValueError):
            unfixable_mask.fix_mask()
        self.assertFalse(unfixable_mask.is_mask)

    def test_bad_data_fail(self):
        """Test that a corrupted file (extra data at end) raises Exception"""
        with self.assertRaises(ValueError):
            mapreader.Map(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_bad_data1.map'))

    def test_bad_data_fail2(self):
        """Test that we can raise an exception with a malformed header"""
        with self.assertRaises(ValueError):
            mapreader.get_data(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_corrupt_header.map'))

    def test_bad_data_fail3(self):
        """Test that we can't have too long a header"""
        with self.assertRaises(ValueError):
            # create a map file with a header larger than 1024 to see the exception
            map = mapreader.get_data(os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.map'))
            for i in range(map._nlabl):
                label = getattr(map, '_label_{}'.format(i))
            y = 11
            for j in range(1, y):
                setattr(map, '_label_{}'.format(j), label)
            map._nlabl = y
            with open('rm.map', 'w') as f:
                map.write(f)

    def test_compute_img_to_phy_transform(self):
        """Compute the transform that aligns the image with the physical space"""
        # only works on local
        # map_file = "/Users/pkorir/Data/segmentations/align_iso_and_seg/emd_5625.map"
        transform = mapreader.compute_transform(self.map_file)
        # transform = mapreader.compute_transform(map_file)
        print(f"\n{transform}")
        # only works on local
        # self.assertTrue(
        #     numpy.array_equal(
        #         numpy.array([
        #             [236.8800048828125/56, 0.0, 0.0, 236.8800048828125/56*(-28)],
        #             [0.0, 236.8800048828125/56, 0.0, 236.8800048828125/56*(-28)],
        #             [0.0, 0.0, 236.8800048828125/56, 236.8800048828125/56*(-28)]
        #         ]),
        #         transform
        #     )
        # )
        self.assertTrue(
            numpy.array_equal(
                numpy.array([
                    [5481.2099609375 / 301, 0.0, 0.0, 0.0],
                    [0.0, 7302.20947265625 / 401, 0.0, 0.0],
                    [0.0, 0.0, 1292.909912109375 / 71, 0.0],
                ]),
                transform
            )
        )

    def test_file_with_full_labels(self):
        """If there are 10 labels then we should be good to go"""
        import pathlib
        map_file = pathlib.Path("/Users/pkorir/Downloads/archive/10087/data/E64_tomo03.mrc")
        if map_file.exists():
            transform = mapreader.compute_transform(map_file)
            self.assertTrue(
                numpy.array_equal(
                    numpy.array([
                        [160., 0, 0, 0],
                        [0, 160., 0, 0],
                        [0, 0, 160., 0],
                    ]),
                    transform
                )
            )


class TestReadersModReader(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mod_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod')
        cls.mod = modreader.get_data(cls.mod_file)

    def test_get_data(self):
        """Test the main entry point: get_data(...)"""
        self.assertTrue(self.mod.isset)
        self.assertGreater(len(self.mod.objts), 0)
        self.assertGreater(self.mod.objt_count, 0)
        self.assertEqual(self.mod.version, 'V1.2')
        self.assertEqual(self.mod.name, 'IMOD-NewModel')
        self.assertGreater(self.mod.xmax, 0)
        self.assertGreater(self.mod.ymax, 0)
        self.assertGreater(self.mod.zmax, 0)
        self.assertGreaterEqual(self.mod.objsize, 1)
        self.assertIn(self.mod.drawmode, [-1, 1])
        self.assertIn(self.mod.mousemode, range(3))  # unclear what 2 is equal to INVALID VALUE
        self.assertIn(self.mod.blacklevel, range(256))
        self.assertIn(self.mod.whitelevel, range(256))
        self.assertEqual(self.mod.xoffset, 0)
        self.assertEqual(self.mod.yoffset, 0)
        self.assertEqual(self.mod.zoffset, 0)
        self.assertGreater(self.mod.xscale, 0)
        self.assertGreater(self.mod.yscale, 0)
        self.assertGreater(self.mod.zscale, 0)
        self.assertGreaterEqual(self.mod.object, 0)
        self.assertGreaterEqual(self.mod.contour, -1)
        self.assertGreaterEqual(self.mod.point, -1)
        self.assertGreaterEqual(self.mod.res, 0)
        self.assertIn(self.mod.thresh, range(256))
        self.assertGreater(self.mod.pixsize, 0)
        self.assertIn(modreader.UNITS[self.mod.units],
                      ['pm', 'ångström', 'nm', 'microns', 'mm', 'cm', 'm', 'pixels', 'km'])
        self.assertIsInstance(self.mod.csum, int)
        self.assertEqual(self.mod.alpha, 0)
        self.assertEqual(self.mod.beta, 0)
        self.assertEqual(self.mod.gamma, 0)

    def test_to_angstrom(self):
        """Test function that converts to ångström"""
        with self.assertRaises(ValueError):
            modreader.angstrom_multiplier(-11)
        self.assertEqual(modreader.angstrom_multiplier(-10), 1)  # ångström
        self.assertEqual(modreader.angstrom_multiplier(-9), 10)  # nm
        self.assertEqual(modreader.angstrom_multiplier(3), 10 ** 13)  # km

    def test_read_fail1(self):
        """Test that file missing 'IMOD' at beginning fails"""
        mod_fn = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_bad_data1.mod')
        with self.assertRaises(ValueError):
            modreader.get_data(mod_fn)  # missing 'IMOD' start

    def test_read_fail2(self):
        """Test that file missing 'IEOF' at end fails"""
        mod_fn = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_bad_data2.mod')
        with self.assertRaises(ValueError):
            modreader.get_data(mod_fn)  # missing 'IEOF' end

    def test_IMOD_pass(self):
        """Test that IMOD chunk read"""
        self.assertTrue(self.mod.isset)
        ijk_to_xyz_transform = self.mod.ijk_to_xyz_transform
        self.assertTrue(ijk_to_xyz_transform[0, 0] * ijk_to_xyz_transform[1, 1] * ijk_to_xyz_transform[2, 2] != 0.0)
        self.assertEqual(self.mod.x_length,
                         self.mod.xmax * self.mod.pixsize * self.mod.xscale * modreader.angstrom_multiplier(
                             self.mod.units))
        self.assertEqual(self.mod.y_length,
                         self.mod.ymax * self.mod.pixsize * self.mod.yscale * modreader.angstrom_multiplier(
                             self.mod.units))
        self.assertEqual(self.mod.z_length,
                         self.mod.zmax * self.mod.pixsize * self.mod.zscale * modreader.angstrom_multiplier(
                             self.mod.units))

    def test_OBJT_pass(self):
        """Test that OBJT chunk read"""
        for objects in _dict_iter_values(self.mod.objts):
            self.assertTrue(objects.isset)

    def test_CONT_pass(self):
        """Test that CONT chunk read"""
        for objects in _dict_iter_values(self.mod.objts):
            for C in _dict_iter_values(objects.conts):
                self.assertTrue(C.isset)

    def test_MESH_pass(self):
        """Test that MESH chunk read"""
        for objects in _dict_iter_values(self.mod.objts):
            for M in _dict_iter_values(objects.meshes):
                self.assertTrue(M.isset)

    def test_IMAT_pass(self):
        """Test that IMAT chunk read"""
        for objects in _dict_iter_values(self.mod.objts):
            self.assertTrue(objects.imat.isset)

    def test_VIEW_pass(self):
        """Test that VIEW chunk read"""
        for views in _dict_iter_values(self.mod.views):
            self.assertTrue(views.isset)

    def test_MINX_pass(self):
        """Test that MINX chunk read"""
        self.assertTrue(self.mod.minx.isset)

    def test_MEPA_pass(self):
        """Test that MEPA chunk read"""
        for objects in _dict_iter_values(self.mod.objts):
            try:
                self.assertTrue(objects.mepa.isset)
            except AttributeError:
                self.assertEqual(objects.mepa, None)

    def test_CLIP_pass(self):
        """Test that CLIP chunk read"""
        for objects in _dict_iter_values(self.mod.objts):
            try:
                self.assertTrue(objects.clip.isset)
            except AttributeError:
                self.assertEqual(objects.clip, None)

    def test_number_of_OBJT_chunks(self):
        """Test that compares declared and found OBJT chunks"""
        self.assertEqual(self.mod.objsize, len(self.mod.objts))

    def test_number_of_CONT_chunks(self):
        """Test that compares declared and found CONT chunks"""
        for objects in _dict_iter_values(self.mod.objts):
            self.assertEqual(objects.contsize, len(objects.conts))

    def test_number_of_MESH_chunks(self):
        """Test that compares declared and found MESH chunks"""
        for objects in _dict_iter_values(self.mod.objts):
            self.assertEqual(objects.meshsize, len(objects.meshes))

    def test_number_of_surface_objects(self):
        """Test that compares declared and found surface objects"""
        for objects in _dict_iter_values(self.mod.objts):
            no_of_surfaces = 0
            for C in _dict_iter_values(objects.conts):
                if C.surf != 0:
                    no_of_surfaces += 1
            self.assertEqual(objects.surfsize, no_of_surfaces)

    def test_number_of_points_in_CONT_chunk(self):
        """Test that compares declared an found points in CONT chunks"""
        for objects in _dict_iter_values(self.mod.objts):
            for C in _dict_iter_values(objects.conts):
                self.assertEqual(C.psize, len(C.pt))

    def test_number_of_vertex_elements_in_MESH_chunk(self):
        """Test that compares declared an found vertices in MESH chunks"""
        for objects in _dict_iter_values(self.mod.objts):
            for M in _dict_iter_values(objects.meshes):
                self.assertEqual(M.vsize, len(M.vert))

    def test_number_of_list_elements_in_MESH_chunk(self):
        """Test that compares declared an found indices in MESH chunks"""
        for objects in _dict_iter_values(self.mod.objts):
            for M in _dict_iter_values(objects.meshes):
                self.assertEqual(M.lsize, len(M.list))


class TestReadersSegReader(Py23FixTestCase):
    def setUp(self):
        super().setUp()
        self.seg_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.seg')

    def test_get_data(self):
        """Test the main entry point: get_data(...)"""
        seg = segreader.get_data(self.seg_file)
        self.assertIsInstance(seg, segreader.SeggerSegmentation)
        self.assertEqual(seg.map_level, 0.852)
        self.assertEqual(seg.format_version, 2)
        self.assertCountEqual(seg.map_size, [26, 27, 30])
        self.assertEqual(seg.format, 'segger')
        self.assertEqual(seg.mask.shape, (30, 27, 26))


class TestReadersStarReader(Py23FixTestCase):
    """Tests for the StarReader class"""

    def test_init(self):
        """Test initialisation"""
        star_reader = starreader.StarReader()
        self.assertIsInstance(star_reader, starreader.StarReader)
        star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data3.star')
        self.assertEqual('7YW1', star_reader.name)
        self.assertTrue(hasattr(star_reader, 'keys'))
        self.assertTrue(hasattr(star_reader, 'tables'))
        self.assertIsInstance(star_reader.keys(), list)
        self.assertIsInstance(star_reader.tables, dict)
        self.assertIsInstance(star_reader.tables['_entity_poly_seq'], starreader.StarTable)
        self.assertIsInstance(star_reader.tables['_entity_poly_seq'].columns, list)
        self.assertTrue('_entity_poly_seq.entity_id' in star_reader.tables['_entity_poly_seq'].columns)
        self.assertEqual(14, len(star_reader.tables['_entity_poly_seq']))
        self.assertTrue(hasattr(star_reader.tables['_entity_poly_seq'], 'prefix'))
        self.assertTrue(hasattr(star_reader.tables['_entity_poly_seq'][0], 'entity_id'))

    def test_parse(self):
        """Test parsing any star file"""
        star_reader = starreader.StarReader()
        # star_reader.parse("/Users/pkorir/Downloads/80S_Ribosomes_particlesfrom_tomomanstopgapwarpmrm_bin1.star")
        star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data2.star')
        print(star_reader.tables['_rln'])

    def test_parse_cif(self):
        """Test that we can parse a cif file"""
        star_reader = starreader.StarReader()
        star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data.cif')
        print(star_reader.tables)
        self.assertEqual('name', star_reader.name)
        self.assertTrue(hasattr(star_reader, 'tables'))
        self.assertTrue(hasattr(star_reader, 'keys'))
        self.assertIsInstance(star_reader.keys(), list)
        self.assertIsInstance(star_reader.tables, dict)
        self.assertIsInstance(star_reader.tables['_atom_site'], starreader.StarTable)
        self.assertIsInstance(star_reader.tables['_atom_site'].columns, list)
        self.assertTrue('_atom_site.id' in star_reader.tables['_atom_site'].columns)
        self.assertEqual(10, len(star_reader.tables['_atom_site']))
        self.assertTrue(hasattr(star_reader.tables['_atom_site'], 'prefix'))
        self.assertTrue(hasattr(star_reader.tables['_atom_site'][0], 'id'))

    def test_parse_relion(self):
        """Test parsing of a relion star file"""
        star_reader = starreader.StarReader()
        self.assertIsInstance(star_reader, starreader.StarReader)
        star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data2.star')
        self.assertTrue(hasattr(star_reader, 'keys'))
        self.assertTrue(hasattr(star_reader, 'tables'))
        self.assertIsInstance(star_reader.keys(), list)
        self.assertIsInstance(star_reader.tables, dict)
        self.assertIsInstance(star_reader.tables['_rln'], starreader.StarTable)
        # print(star_reader.tables['_rln'])
        self.assertEqual(6, len(star_reader.tables['_rln']))
        row = star_reader.tables['_rln'][0]
        # print(f"type(row) = {type(row)}")
        # print(repr(row))
        self.assertIsInstance(row, starreader.StarTableRow)
        # for row in star_reader.tables['_rln']:
        #     print(row)
        #     print(row.Magnification)
        # check that we can access the attributes
        for attr in star_reader.tables['_rln'].columns:
            self.assertTrue(hasattr(star_reader.tables['_rln'][0], attr.replace('_rln', '')))
        # print(star_reader.tables['_rln'][0][4])
        self.assertEqual(917.89670, star_reader.tables['_rln'][0][4])

    def test_relion_header(self):
        """Test that we have a header attribute to create the field names on a dime"""
        relion_star_reader = starreader.RelionStarReader(image_name_field='_rlnTomoName')
        relion_star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data8.star')
        self.assertTrue(hasattr(relion_star_reader.tables['_rln'], 'header'))
        # each table should have a `header` attribute which can recreate the table header
        # e.g. table.header -> `loop_\n_rlnCoordinateX #1\n_rlnCoordinateY #2\n_rlnCoordinateZ #3\n` etc.
        # print()
        # print(relion_star_reader.tables['_rln'].header)
        # for row in relion_star_reader.tables['_rln']:
        #     print(row.raw_data())
        self.assertEqual(
            relion_star_reader.tables['_rln'].header,
            """loop_
_rlnMagnification
_rlnDetectorPixelSize
_rlnCoordinateX
_rlnCoordinateY
_rlnCoordinateZ
_rlnAngleRot
_rlnAngleTilt
_rlnAnglePsi
_rlnTomoName
_rlnCtfImage
_rlnRandomSubset
_rlnPixelSize
_rlnVoltage
_rlnSphericalAberration
_rlnMicrographName"""
        )

    def test_relion_reader_column_validation(self):
        """Test the constraints for a relion star file"""
        relion_star_reader = starreader.RelionStarReader()
        # test that all required columns are present
        with self.assertRaisesRegex(ValueError, r".*Loop header is missing.*"):
            relion_star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data5.star')

    def test_relion_reader_duplicate_table_validation(self):
        """Test that only one table is present"""
        relion_star_reader = starreader.RelionStarReader()
        with self.assertRaises(RuntimeError):  # if the table is just a repeat
            relion_star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data6.star')

    def test_relion_reader_table_count_validation(self):
        """Test that only one table is present"""
        relion_star_reader = starreader.RelionStarReader()
        with self.assertRaises(ValueError, msg="Maximum number of tables exceeded"):  # if the table is just a repeat
            relion_star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data7.star')

    def test_relion_reader_one_tomogram_validation(self):
        """Test that we have only one tomogram"""
        relion_star_reader = starreader.RelionStarReader()
        with self.assertRaises(ValueError, msg="STAR file references more than one tomogram. Please perform "
                                               "preprocessing to split STAR file to individual files referencing "
                                               "only one tomogram."):
            relion_star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data2.star')

    def test_compute_affine_transforms(self):
        """Test StarTableRow"""
        star_reader = starreader.StarReader()
        star_reader.parse(TEST_DATA_PATH / 'segmentations' / 'test_data4.star')
        row = star_reader.tables['_rln'][0]
        print()
        print(row)
        transform_zyz = row.to_affine_transform()  # default axes
        print(transform_zyz)
        psi = radians(30)
        theta = radians(30)
        phi = radians(30)
        # zyz euler angles
        affine_matrix_zyz = numpy.array([
            [cos(psi) * cos(theta) * cos(phi) - sin(psi) * sin(phi),
             -sin(psi) * cos(theta) * cos(phi) - cos(psi) * sin(phi), sin(theta) * cos(phi)],
            [cos(psi) * cos(theta) * sin(phi) + sin(psi) * cos(phi),
             -sin(psi) * cos(theta) * sin(phi) + cos(psi) * cos(phi), sin(theta) * sin(phi)],
            [-cos(psi) * sin(theta), sin(psi) * sin(theta), cos(theta)]
        ])
        # rotation
        self.assertTrue(
            numpy.allclose(transform_zyz[:3, :3], affine_matrix_zyz)
        )
        # translation
        self.assertEqual(487.84700, transform_zyz[0, 3])
        self.assertEqual(2451.94100, transform_zyz[1, 3])
        self.assertEqual(917.89670, transform_zyz[2, 3])
        # ZXZ euler angles
        transform_zxz = row.to_affine_transform(axes='zxz')
        # zxz euler angles
        affine_matrix_zxz = numpy.array([
            [
                cos(psi) * cos(phi) - cos(theta) * sin(psi) * sin(phi),
                -cos(psi) * sin(phi) - cos(phi) * cos(theta) * sin(psi),
                sin(psi) * sin(theta)
            ],
            [
                cos(phi) * sin(psi) + cos(psi) * cos(theta) * sin(phi),
                cos(psi) * cos(theta) * cos(phi) - sin(psi) * sin(phi),
                -cos(psi) * sin(theta)],
            [
                sin(theta) * sin(phi),
                cos(phi) * sin(theta),
                cos(theta)
            ]
        ])
        self.assertTrue(
            numpy.allclose(transform_zxz[:3, :3], affine_matrix_zxz)
        )

    def test_regex_float(self):
        """Test the regex for a floating point number"""
        float_re1 = starreader.FLOAT_RE1
        float_re2 = starreader.FLOAT_RE2
        float_re3 = starreader.FLOAT_RE3
        floats = ['1.0', '1.', '.1', '1.0e-1', '1.0E-1', '1.0e+1', '1.0E+1', '1.0e1', '1.0E1', '1.0e+01', '1.0E+01',
                  '1.0e-01', '1.0E-01', '1.0e-1',
                  '1.0E-1', '1.0e+1', '-1.0', '-1.']
        nonfloats = ['4-4', '3.4.2', '3.4e', '3.4E', '3.4e+', '3.4E+', '3.4e-', '3.4E-', ]
        # self.assertTrue(re.match(float_re1, str(floats[1])))
        for f in floats:
            # print(f)
            self.assertTrue(re.match(float_re1, f))
            self.assertTrue(re.match(float_re2, f) or re.match(float_re3, f))
        for n in nonfloats:
            # print(n)
            self.assertFalse(re.match(float_re1, n))
            self.assertFalse(re.match(float_re2, n) and re.match(float_re3, n))

    def test_regex_int(self):
        """Test the regex for an integer"""
        int_re = starreader.INT_RE
        ints = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-1', '-2', '-3', '-4', '-5', '-6', '-7', '-8', '-9',
                '-0']
        nonints = ['1.0', '1.', '.1', '1.0e-1', '1.0E-1', '1.0e+1', '1.0E+1', '1.0e1', '1.0E1', '1.0e+01', '1.0E+01',
                   '1.0e-01', '1.0E-01', '1.0e-1',
                   '1.0E-1', '1.0e+1', '4-4', '3.4.2', '3.4e', '3.4E', '3.4e+', '3.4E+', '3.4e-', '3.4E-', 'paul',
                   'None']
        for i in ints:
            # print(i)
            self.assertTrue(re.match(int_re, i))
        for n in nonints:
            # print(n)
            self.assertFalse(re.match(int_re, n))


class TestReadersStlReader(Py23FixTestCase):
    def setUp(self):
        super().setUp()
        self.stl_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.stl')
        self.stl_bin_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_binary.stl')
        self.stl_multi_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data_multiple.stl')

    def test_get_data(self):
        """Test the main entry point: get_data(...)"""
        meshes = stlreader.get_data(self.stl_file)  # only one mesh here
        name, vertices, polygons = meshes[0]
        num_vertices = len(vertices)
        a, b, c = zip(*polygons.values())
        vertex_ids = set(a + b + c)
        self.assertEqual(name, "{}#{}".format(os.path.basename(self.stl_file), 0))
        self.assertGreaterEqual(num_vertices, 1)
        self.assertEqual(min(vertex_ids), min(vertices.keys()))
        self.assertEqual(max(vertex_ids), max(vertices.keys()))
        self.assertEqual(sum(set(vertex_ids)), sum(vertices.keys()))
        self.assertEqual(set(vertex_ids), set(vertices.keys()))

    def test_read_binary(self):
        """Test that we can read a binary STL file"""
        meshes = stlreader.get_data(self.stl_bin_file)
        name, vertices, polygons = meshes[0]
        self.assertEqual(name, "{}#{}".format(os.path.basename(self.stl_bin_file), 0))
        self.assertTrue(len(vertices) > 0)
        self.assertTrue(len(polygons) > 0)
        polygon_ids = list()
        for a, b, c in _dict_iter_values(polygons):
            polygon_ids += [a, b, c]
        self.assertCountEqual(set(vertices.keys()), set(polygon_ids))

    def test_read_multiple(self):
        """Test that we can read a multi-solid STL file

        Only works for ASCII by concatenation"""
        meshes = stlreader.get_data(self.stl_multi_file)
        for name, vertices, polygons in meshes:
            self.assertEqual(name, "{}#{}".format(os.path.basename(self.stl_multi_file), 0))
            self.assertTrue(len(vertices) > 0)
            self.assertTrue(len(polygons) > 0)
            polygon_ids = list()
            for a, b, c in _dict_iter_values(polygons):
                polygon_ids += [a, b, c]
            self.assertCountEqual(set(vertices.keys()), set(polygon_ids))

    def test_compute_bounding_box(self):
        """Test that we can compute the bounding box of an STL file"""
        test_stl_file = TEST_DATA_PATH / 'segmentations' / 'test_data.stl'
        x, y, z = stlreader.compute_bounding_box(test_stl_file)
        self.assertAlmostEqual(x[0], 89.08, places=3)
        self.assertAlmostEqual(x[1], 271.337, places=3)
        self.assertAlmostEqual(y[0], 78.1158, places=3)
        self.assertAlmostEqual(y[1], 266.757, places=3)
        self.assertAlmostEqual(z[0], 100.887, places=3)
        self.assertAlmostEqual(z[1], 240.9, places=3)


class TestReadersSurfReader(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.surf_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.surf')
        cls.header, cls.segments = surfreader.get_data(cls.surf_file)  # only one mesh here

    def test_get_data(self):
        """Test the main entry point: get_data(...)"""
        name = self.segments[2][0].name
        vertices = self.segments[2][0].vertices
        triangles = self.segments[2][0].triangles
        num_vertices = len(vertices)
        a, b, c = zip(*triangles)
        vertex_ids = set(a + b + c)
        self.assertIsInstance(self.header, ahds.header.AmiraHeader)
        self.assertIsInstance(self.segments, dict)
        self.assertEqual(name, 'medulla_r')
        self.assertGreaterEqual(num_vertices, 1)
        self.assertGreaterEqual(len(self.segments), 1)
        self.assertEqual(min(vertex_ids), min(vertices.keys()))
        self.assertEqual(max(vertex_ids), max(vertices.keys()))
        self.assertEqual(sum(set(vertex_ids)), sum(vertices.keys()))
        self.assertEqual(set(vertex_ids), set(vertices.keys()))


class TestReadersSurvosReader(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.survos_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.h5')
        cls.survos_complex_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_complex_survos.h5')

    def test_get_data(self):
        """Test the main entry point"""
        result = survosreader.get_data(self.survos_file)
        self.assertIsInstance(result, survosreader.SuRVoSSegmentation)
        self.assertIsInstance(result.data, numpy.ndarray)
        ids = result.segment_ids()
        self.assertIsInstance(ids, frozenset)
        self.assertFalse(-1 in ids)  # 0 is an invalid segment marker
        # attributes are empty lists: colours, labels, names
        self.assertEqual(0, len(result.names))
        self.assertEqual(2, len(result.labels))
        self.assertEqual(0, len(result.colours))

    def test_get_complex_data(self):
        """Test survos file with extra attributes"""
        result = survosreader.get_data(self.survos_complex_file)
        self.assertIsInstance(result, survosreader.SuRVoSSegmentation)
        self.assertIsInstance(result.data, numpy.ndarray)
        # attributes: colours, labels, names
        self.assertTrue(len(result.names) > 0)
        self.assertTrue(len(result.labels) > 0)
        self.assertTrue(len(result.colours) > 0)

    def test_SuRVoSSegmentation(self):
        """Tests for the SuRVoSSegmentation class"""
        surv = survosreader.SuRVoSSegmentation(self.survos_file)
        with self.assertRaises(KeyError):
            _ = survosreader.SuRVoSSegmentation(self.survos_file, dataset='/something')
        with self.assertRaises(ValueError):
            _ = surv['a']
        with self.assertRaises(ValueError):
            _ = surv[0.1]
        with self.assertRaises(IndexError):
            _ = surv[10]
        self.assertIsInstance(surv.shape, tuple)
        ids = list(surv.segment_ids())
        # let's get a portion from the 66-th z at the bottom-right corner
        _s = 66, slice(125, 140), slice(125, 140)
        self.stderr(surv.data[_s])
        seg1 = surv[ids[0]]
        self.stderr(seg1[_s])
        seg2 = surv[ids[1]]
        self.stderr(seg2[_s])
        self.assertEqual(seg1.shape, surv.shape)
        self.assertEqual(seg2.shape, surv.shape)


if __name__ == "__main__":
    unittest.main()
