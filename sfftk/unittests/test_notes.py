#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for :py:mod:`sfftk.core.notes` package"""

from __future__ import division

import os
import re
import shlex
import sys
import unittest

import h5py

import __init__ as tests

from .. import schema
from ..core.parser import parse_args
from ..notes import view, modify, find


__author__  = "Paul K. Korir, PhD"
__email__   = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__    = "2017-05-15"
 
# :TODO: rewrite to use sfftk.notes.modify.SimpleNote
 
class TestNotes_view(unittest.TestCase):
    def setUp(self):
        self.segment_id = 15559
        self.sff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff')
    def test_list_default(self):
        """Test that we can view the list of segmentations with annotations"""
        args = parse_args(shlex.split("notes list {}".format(
            self.sff_file
            )))
        status = view.list_notes(args)
        # assertions
        self.assertEqual(status, 0)
    def test_long_list(self):
        """Test that we can long list (-l) the list of segmentations with annotations"""
        args = parse_args(shlex.split("notes list -l {}".format(
            self.sff_file
            )))
        status = view.list_notes(args)
        # assertions
        self.assertEqual(status, 0)
    def test_show_default(self):
        """Test that we can show annotations in a single segment"""
        args = parse_args(shlex.split("notes show -i {} {}".format(
            self.segment_id,
            self.sff_file
            )))
        status = view.show_notes(args)
        self.assertEqual(status, 0)
    def test_long_show(self):
        """Test that we can show in long format annotations in a single segment"""
        args = parse_args(shlex.split("notes show -l -i {} {}".format(
            self.segment_id,
            self.sff_file
            )))
        status = view.show_notes(args)
        self.assertEqual(status, 0)
   
  
class TestNotes_modify(unittest.TestCase):
    # test filetypeA to filetypeB
    def setUp(self):
        self.segment_id = 15559
    def _test_add(self):
        """Test that we can add a note to an .sff (XML) file"""
        desc = 'a short description'
        num = tests._random_integer()
        extref = ['lsfj', 'sljfs']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        cmd = shlex.split("notes add -i {} -D '{}' -E {} -n {} -C {} -M {} {}".format(
            self.segment_id, 
            desc, 
            " ".join(extref), 
            num, 
            ','.join(complexes),
            ','.join(macromolecules),
            self.sff_file)
            )
        args = parse_args(cmd)
        status = modify.add_note(args)
        seg = schema.SFFSegmentation(self.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status, 0)
        self.assertEqual(segment.biologicalAnnotation.description, desc)
        self.assertEqual(segment.biologicalAnnotation.numberOfInstances, num)
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].type, extref[0])
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].value, extref[1])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[0], complexes[0])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[1], complexes[1])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[2], complexes[2])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[0], macromolecules[0])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[1], macromolecules[1])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[2], macromolecules[2])
    def _test_edit(self):
        """Test that we can edit a note in an .sff (XML) file"""
        desc = 'a short description'
        num = tests._random_integer()
        extref = ['lsfj', 'sljfs']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        cmd = shlex.split("notes add -i {} -D '{}' -E {} -n {} -C {} -M {} {}".format(
            self.segment_id, 
            desc, 
            " ".join(extref), 
            num, 
            ','.join(complexes),
            ','.join(macromolecules),
            self.sff_file)
            )
        args = parse_args(cmd)
        # add
        modify.add_note(args)
        desc1 = desc[::-1]
        num1 = tests._random_integer()
        extref1 = map(lambda e: e[::-1], extref)
        cmd1 = shlex.split("notes edit -i {} -D '{}' -e 0 -E {} -n {} -c 1 -C {} -m 2 -M {} {}".format(
            self.segment_id,
            desc1,
            " ".join(extref1),
            num1,
            complexes[1][::-1],
            macromolecules[2][::-1],
            self.sff_file
            ))
        args1 = parse_args(cmd1)
        # edit
        status1 = modify.edit_note(args1)
        seg = schema.SFFSegmentation(self.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status1, 0)
        self.assertEqual(segment.biologicalAnnotation.description, desc1)
        self.assertEqual(segment.biologicalAnnotation.numberOfInstances, num1)
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].type, extref1[0])
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].value, extref1[1])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[1], complexes[1][::-1])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[2], macromolecules[2][::-1])
    def _test_del(self):
        """Test that we can delete a note from an .sff (XML) file"""
        desc = 'a short description'
        num = tests._random_integer()
        extref = ['lsfj', 'sljfs']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        cmd = shlex.split("notes add -i {} -D '{}' -E {} -n {} -C {} -M {} {}".format(
            self.segment_id, 
            desc, 
            " ".join(extref), 
            num, 
            ','.join(complexes),
            ','.join(macromolecules),
            self.sff_file
            ))
        args = parse_args(cmd)
        # add
        modify.add_note(args)
        # delete
        cmd1 = shlex.split("notes del -i {} -D -e 0 -n -c 0 -m 1 {}".format(
            self.segment_id,
            self.sff_file
            ))
        args1 = parse_args(cmd1)
        status1 = modify.del_note(args1)
        seg = schema.SFFSegmentation(self.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status1, 0)
        self.assertIsNone(segment.biologicalAnnotation.description)
        self.assertIsNone(segment.biologicalAnnotation.numberOfInstances)
        self.assertEqual(len(segment.biologicalAnnotation.externalReferences), 0)
        self.assertEqual(len(segment.complexesAndMacromolecules.complexes), 2)
        self.assertEqual(len(segment.complexesAndMacromolecules.macromolecules), 2)
 
 
class TestNotes_modify_sff(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_sff, self).setUp()
        self.sff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff')
    def tearDown(self):
        seg = schema.SFFSegmentation(self.sff_file)
        # remove all annotations
        for segment in seg.segments:
            segment.biologicalAnnotation = schema.SFFBiologicalAnnotation()
            segment.complexesAndMacromolecules = schema.SFFComplexesAndMacromolecules()
        seg.export(self.sff_file)
    def test_add(self):
        super(TestNotes_modify_sff, self)._test_add()
    def test_edit(self):
        super(TestNotes_modify_sff, self)._test_edit()
    def test_del(self):
        super(TestNotes_modify_sff, self)._test_del()
  

"""
:FIXME: hff tests work but quadruple size of file
"""
# class TestNotes_modify_hff(TestNotes_modify):
#     def setUp(self):
#         super(TestNotes_modify_hff, self).setUp()
#         self.sff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.hff')
#     def tearDown(self):
#         with h5py.File(self.sff_file) as h:
#             seg = schema.SFFSegmentation.from_hff(h)
#             # remove all annotations
#             for segment in seg.segments:
#                 segment.biologicalAnnotation = schema.SFFBiologicalAnnotation()
#                 segment.complexesAndMacromolecules = schema.SFFComplexesAndMacromolecules()
#         seg.export(self.sff_file)
#     def test_add(self):
#         super(TestNotes_modify_hff, self)._test_add()
#     def test_edit(self):
#         super(TestNotes_modify_hff, self)._test_edit()
#     def test_del(self):
#         super(TestNotes_modify_hff, self)._test_del()
 
  
class TestNotes_modify_json(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_json, self).setUp()
        self.sff_file = os.path.join(tests.TEST_DATA_PATH, 'sff', 'emd_1014.sff')
    def tearDown(self):
        seg = schema.SFFSegmentation(self.sff_file)
        # remove all annotations
        for segment in seg.segments:
            segment.biologicalAnnotation = schema.SFFBiologicalAnnotation()
            segment.complexesAndMacromolecules = schema.SFFComplexesAndMacromolecules()
        seg.export(self.sff_file)
    def test_add(self):
        super(TestNotes_modify_json, self)._test_add()
    def test_edit(self):
        super(TestNotes_modify_json, self)._test_edit()
    def test_del(self):
        super(TestNotes_modify_json, self)._test_del()
         
 
class TestNotes_find(unittest.TestCase):
    def test_search_default(self):
        """Test default search parameters"""
        args = parse_args(shlex.split("notes search 'mitochondria'"))
        query = find.SearchQuery(args)
        results = query.search()
        self.assertGreater(len(results), 0)
    def test_search_no_results(self):
        """Test search that returns no results"""
        # I'm not sure when some biological entity with such a name will be discovered!
        args = parse_args(shlex.split("notes search 'nothing' --exact"))
        query = find.SearchQuery(args)
        results = query.search()
        self.assertEqual(len(results), 0)
    def test_search_exact_result(self):
        """Test that we get an exact result
            
        NOTE: this test is likely to break as the ontologies get updated
        """
        # this usually returns a single result
        args = parse_args(shlex.split("notes search 'DNA replication licensing factor MCM6' --exact"))
        query = find.SearchQuery(args)
        results = query.search()
        self.assertEqual(len(results), 2) # funny! 
    def test_search_ontology(self):
        """Test that we can search an ontology"""
        # this search should bring at least one result
        args = parse_args(shlex.split("notes search 'mitochondria' --exact -O omit"))
        query = find.SearchQuery(args)
        results = query.search()
        self.assertGreaterEqual(len(results), 1)
    def test_search_from_start(self):
        """Test that we can search from the starting index"""
        # this search usually has close to 1000 results; 100 is a reasonable start
        random_start = tests._random_integer(1, 970)
        args = parse_args(shlex.split("notes search 'mitochondria' --start {}".format(
            random_start
            )))
        query = find.SearchQuery(args)
        results = query.search()
        self.assertGreaterEqual(results._str_result['response']['start'], random_start - 1)
    def test_search_result_rows(self):
        """Test that we get as many result rows as specified"""
        # this search usually has close to 1000 results; 100 is a reasonable start
        random_rows = tests._random_integer(10, 100)
        args = parse_args(shlex.split("notes search 'mitochondria' --rows {}".format(
            random_rows
            )))
        query = find.SearchQuery(args)
        results = query.search()
        self.assertGreaterEqual(len(results._str_result['response']['docs']), random_rows)
        


if __name__ == "__main__":
    unittest.main()