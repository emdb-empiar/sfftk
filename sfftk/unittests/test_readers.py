#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
sfftk.unittests.test_readers

This testing module should have no side-effects because it only reads.
'''

from __future__ import division

import glob
import os
import sys
import unittest

import ahds
import numpy

import __init__ as tests

from ..readers import amreader, mapreader, modreader, segreader, stlreader, surfreader


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-05-15"
__updated__ = '2018-02-14'


# readers
class TestReaders_amreader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.am_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.am')
        cls.header, cls.segments_by_stream = amreader.get_data(cls.am_file)

    def test_get_data(self):
        '''Test the main entry point: get_data(...)'''
        self.assertIsInstance(self.header, ahds.header.AmiraHeader)
        self.assertIsInstance(self.segments_by_stream, numpy.ndarray)
        self.assertGreaterEqual(len(self.segments_by_stream), 1)

    def test_first_line_amiramesh(self):
        '''test that it's declared as an AmiraMesh file'''
        self.assertEqual(self.header.designation.filetype, 'AmiraMesh')

    def test_first_line_binary_little_endian(self):
        '''test that it is formatted as BINARY-LITTLE-ENDIAN'''
        self.assertEqual(self.header.designation.format, 'BINARY-LITTLE-ENDIAN')

    def test_first_line_version(self):
        '''test that it is version 2.1'''
        self.assertEqual(self.header.designation.version, '2.1')

    def test_lattice_present(self):
        '''test Lattice definition exists in definitions'''
        self.assertTrue('Lattice' in self.header.definitions.attrs)

    def test_materials_present(self):
        '''test Materials exist in parameters'''
        self.assertIsNotNone('Materials' in self.header.parameters.attrs)


class TestReaders_mapreader(unittest.TestCase):
    def setUp(self):
        self.map_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.map')

    def test_get_data(self):
        '''Test the main entry point: get_data(...)'''
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
        self.assertIsInstance(map_._machst, int)
        self.assertGreater(map_._rms, 0)
        self.assertGreater(map_._nlabl, 0)

    def test_write(self):
        '''Test write map file'''
        map_to_write = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_write_map.map')
        written_maps = glob.glob(map_to_write)
        self.assertEqual(len(written_maps), 0)
        with open(map_to_write, 'w') as f:
            map_ = mapreader.get_data(self.map_file)
            map_.write(f)
        written_maps = glob.glob(map_to_write)
        self.assertEqual(len(written_maps), 1)
        map(os.remove, written_maps)

    def test_invert(self):
        '''Test invert map intensities'''
        map_ = mapreader.get_data(self.map_file, inverted=False)
        self.assertFalse(map_._inverted)
        map_.invert()
        self.assertTrue(map_._inverted)
        map_ = mapreader.get_data(self.map_file, inverted=True)
        self.assertTrue(map_._inverted)

    def test_fix_mask(self):
        '''Test fix mask for fixable mask'''
        fixable_mask = mapreader.Map(os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_fixable_mask.map'))
        self.assertFalse(fixable_mask.is_mask)
        fixable_mask.fix_mask()
        self.assertTrue(fixable_mask.is_mask)

    def test_unfixable_mask(self):
        '''Test exception for unfixable mask'''
        unfixable_mask = mapreader.Map(os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_unfixable_mask.map'))
        self.assertFalse(unfixable_mask.is_mask)
        with self.assertRaises(ValueError):
            unfixable_mask.fix_mask()
        self.assertFalse(unfixable_mask.is_mask)

    def test_bad_data_fail(self):
        '''Test that a corrupted file (extra data at end) raises Exception'''
        with self.assertRaises(ValueError):
            mapreader.Map(os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_bad_data1.map'))


class TestReaders_modreader(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.mod_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.mod')
        cls.mod = modreader.get_data(cls.mod_file)

    def test_get_data(self):
        '''Test the main entry point: get_data(...)'''
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
        self.assertIn(self.mod.units, ['pm', 'Angstroms', 'nm', 'microns', 'mm', 'cm', 'm', 'pixels', 'km'])
        self.assertIsInstance(self.mod.csum, int)
        self.assertEqual(self.mod.alpha, 0)
        self.assertEqual(self.mod.beta, 0)
        self.assertEqual(self.mod.gamma, 0)

    def test_read_fail1(self):
        '''Test that file missing 'IMOD' at beginning fails'''
        mod_fn = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_bad_data1.mod')
        with self.assertRaises(ValueError):
            modreader.get_data(mod_fn)  # missing 'IMOD' start

    def test_read_fail2(self):
        '''Test that file missing 'IEOF' at end fails'''
        mod_fn = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_bad_data2.mod')
        with self.assertRaises(ValueError):
            modreader.get_data(mod_fn)  # missing 'IEOF' end

    def test_IMOD_pass(self):
        '''Test that IMOD chunk read'''
        self.assertTrue(self.mod.isset)

    def test_OBJT_pass(self):
        '''Test that OBJT chunk read'''
        for O in self.mod.objts.itervalues():
            self.assertTrue(O.isset)

    def test_CONT_pass(self):
        '''Test that CONT chunk read'''
        for O in self.mod.objts.itervalues():
            for C in O.conts.itervalues():
                self.assertTrue(C.isset)

    def test_MESH_pass(self):
        '''Test that MESH chunk read'''
        for O in self.mod.objts.itervalues():
            for M in O.meshes.itervalues():
                self.assertTrue(M.isset)

    def test_IMAT_pass(self):
        '''Test that IMAT chunk read'''
        for O in self.mod.objts.itervalues():
            self.assertTrue(O.imat.isset)

    def test_VIEW_pass(self):
        '''Test that VIEW chunk read'''
        for V in self.mod.views.itervalues():
            self.assertTrue(V.isset)

    def test_MINX_pass(self):
        '''Test that MINX chunk read'''
        self.assertTrue(self.mod.minx.isset)

    def test_MEPA_pass(self):
        '''Test that MEPA chunk read'''
        for O in self.mod.objts.itervalues():
            try:
                self.assertTrue(O.mepa.isset)
            except AttributeError:
                self.assertEqual(O.mepa, None)

    def test_CLIP_pass(self):
        '''Test that CLIP chunk read'''
        for O in self.mod.objts.itervalues():
            try:
                self.assertTrue(O.clip.isset)
            except AttributeError:
                self.assertEqual(O.clip, None)

    def test_number_of_OBJT_chunks(self):
        '''Test that compares declared and found OBJT chunks'''
        self.assertEqual(self.mod.objsize, len(self.mod.objts))

    def test_number_of_CONT_chunks(self):
        '''Test that compares declared and found CONT chunks'''
        for O in self.mod.objts.itervalues():
            self.assertEqual(O.contsize, len(O.conts))

    def test_number_of_MESH_chunks(self):
        '''Test that compares declared and found MESH chunks'''
        for O in self.mod.objts.itervalues():
            self.assertEqual(O.meshsize, len(O.meshes))

    def test_number_of_surface_objects(self):
        '''Test that compares declared and found surface objects'''
        for O in self.mod.objts.itervalues():
            no_of_surfaces = 0
            for C in O.conts.itervalues():
                if C.surf != 0:
                    no_of_surfaces += 1
            self.assertEqual(O.surfsize, no_of_surfaces)

    def test_number_of_points_in_CONT_chunk(self):
        '''Test that compares declared an found points in CONT chunks'''
        for O in self.mod.objts.itervalues():
            for C in O.conts.itervalues():
                self.assertEqual(C.psize, len(C.pt))

    def test_number_of_vertex_elements_in_MESH_chunk(self):
        '''Test that compares declared an found vertices in MESH chunks'''
        for O in self.mod.objts.itervalues():
            for M in O.meshes.itervalues():
                self.assertEqual(M.vsize, len(M.vert))

    def test_number_of_list_elements_in_MESH_chunk(self):
        '''Test that compares declared an found indices in MESH chunks'''
        for O in self.mod.objts.itervalues():
            for M in O.meshes.itervalues():
                self.assertEqual(M.lsize, len(M.list))


class TestReaders_segreader(unittest.TestCase):
    def setUp(self):
        self.seg_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.seg')

    def test_get_data(self):
        '''Test the main entry point: get_data(...)'''
        seg = segreader.get_data(self.seg_file)
        print >> sys.stderr, seg
        self.assertIsInstance(seg, segreader.SeggerSegmentation)
        self.assertEqual(seg.map_level, 0.852)
        self.assertEqual(seg.format_version, 2)
        self.assertItemsEqual(seg.map_size, [26, 27, 30])
        self.assertEqual(seg.format, 'segger')
        self.assertEqual(seg.mask.shape, (30, 27, 26))


class TestReaders_stlreader(unittest.TestCase):
    def setUp(self):
        self.stl_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.stl')
        self.stl_bin_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data_binary.stl')
        self.stl_mult_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data_multiple.stl')

    def test_get_data(self):
        '''Test the main entry point: get_data(...)'''
        meshes = stlreader.get_data(self.stl_file)  #  only one mesh here
        name, vertices, polygons = meshes[0]
        num_vertices = len(vertices)
        a, b, c = zip(*polygons.values())
        vertex_ids = set(a + b + c)
        self.assertIsNone(name)
        self.assertGreaterEqual(num_vertices, 1)
        self.assertEqual(min(vertex_ids), min(vertices.keys()))
        self.assertEqual(max(vertex_ids), max(vertices.keys()))
        self.assertEqual(sum(set(vertex_ids)), sum(vertices.keys()))
        self.assertEqual(set(vertex_ids), set(vertices.keys()))

    def test_read_binary(self):
        '''Test that we can read a binary STL file'''
        meshes = stlreader.get_data(self.stl_bin_file)
        print >> sys.stderr, meshes[0][0]
        name, vertices, polygons = meshes[0]
        self.assertIsNone(name)
        self.assertTrue(len(vertices) > 0)
        self.assertTrue(len(polygons) > 0)
        polygon_ids = list()
        for a, b, c in polygons.itervalues():
            polygon_ids += [a, b, c]
        self.assertItemsEqual(set(vertices.keys()), set(polygon_ids))

    def test_read_multiple(self):
        '''Test that we can read a multi-solid STL file
          
        Only works for ASCII by concatenation'''
        meshes = stlreader.get_data(self.stl_mult_file)
        for name, vertices, polygons in meshes:
            self.assertIsNone(name)
            self.assertTrue(len(vertices) > 0)
            self.assertTrue(len(polygons) > 0)
            polygon_ids = list()
            for a, b, c in polygons.itervalues():
                polygon_ids += [a, b, c]
            self.assertItemsEqual(set(vertices.keys()), set(polygon_ids))


class TestReaders_surfreader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.surf_file = os.path.join(tests.TEST_DATA_PATH, 'segmentations', 'test_data.surf')
        cls.header, cls.segments = surfreader.get_data(cls.surf_file)  #  only one mesh here

    def test_get_data(self):
        '''Test the main entry point: get_data(...)'''
        name = self.segments[2].name
        vertices = self.segments[2].vertices
        triangles = self.segments[2].triangles
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


if __name__ == "__main__":
    unittest.main()
