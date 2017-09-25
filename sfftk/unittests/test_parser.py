# test_parser.py
# -*- coding: utf-8 -*-
"""Unit tests for :py:mod:`sfftk.core.parser` module"""
from __future__ import division

__author__  = 'Paul K. Korir, PhD'
__email__   = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__    = '2016-06-10'

import sys
import os
import shlex
import unittest

from ..core.parser import parse_args
from ..core.configs import get_configs
from . import TEST_DATA_PATH, _random_float, _random_integer

configs = get_configs()


# redirect sys.stderr/sys.stdout to /dev/null
# from: http://stackoverflow.com/questions/8522689/how-to-temporary-hide-stdout-or-stderr-while-running-a-unittest-in-python
# _stderr = sys.stderr
# _stdout = sys.stdout
# null = open(os.devnull, 'wb')
# sys.stdout = null
# sys.stderr = null

"""
:FIXME: use shlex.split(cmd) for proper splitting of quoted strings
"""

class TestParser_convert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print >> sys.stderr, "convert tests..."
        cls.test_data_file = os.path.join(TEST_DATA_PATH, 'segmentations', 'test_data.mod')
        
    @classmethod
    def tearDownClass(cls):
        print >> sys.stderr, ""
        
    def test_default(self):
        """Test convert parser"""
        args = parse_args(shlex.split('convert {}'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.subcommand, 'convert')
        self.assertEqual(args.from_file, self.test_data_file)
        self.assertEqual(args.output, os.path.join(os.path.dirname(self.test_data_file), 'test_data.sff'))
        self.assertEqual(args.primary_descriptor, None)
        self.assertFalse(args.verbose)
#         self.assertFalse(args.exclude_unannotated_regions)
        self.assertFalse(args.contours_to_mesh)
        
    def test_details(self):
        """Test convert parser with details"""
        args = parse_args(shlex.split('convert -d "Some details" {}'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.details, 'Some details')
        
    def test_contours_to_mesh(self):
        """Test convert parser contours to mesh"""
        args = parse_args(shlex.split('convert -M {}'.format(self.test_data_file)))
        # assertions
        self.assertTrue(args.contours_to_mesh)
        
    def test_output_sff(self):
        """Test convert parser to .sff"""
        args = parse_args(shlex.split('convert {} -o file.sff'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.output, 'file.sff')
        
    def test_output_hff(self):
        """Test convert parser to .hff"""
        args = parse_args(shlex.split('convert {} -o file.hff'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.output, 'file.hff')
        
    def test_output_json(self):
        """Test convert parser to .json"""
        args = parse_args(shlex.split('convert {} -o file.json'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.output, 'file.json')
        
    def test_primary_descriptor(self):
        """Test convert parser with primary_descriptor"""
        args = parse_args(shlex.split('convert -P threeDVolume {}'.format(self.test_data_file)))
        # assertions
        self.assertEqual(args.primary_descriptor, 'threeDVolume')
    
    def test_wrong_primary_descriptor_fails(self):
        """Test that we have a check on primary descriptor values"""
        # assertions
        with self.assertRaises(ValueError):
            parse_args(shlex.split('convert -P something {}'.format(self.test_data_file)))
        
    def test_verbose(self):
        """Test convert parser with verbose"""
        args = parse_args(shlex.split('convert -v {}'.format(self.test_data_file)))
        # assertions
        self.assertTrue(args.verbose)
        
#     def test_exclude_unannotated_regions(self):
#         """Test that we set the exclude unannotated regions flag"""
#         args = parse_args(shlex.split('convert -x {}'.format(self.test_data_file)))
#         # assertions
#         self.assertTrue(args.exclude_unannotated_regions)


class TestParser_view(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print >> sys.stderr, "view tests..."
        
    @classmethod
    def tearDownClass(cls):
        print >> sys.stderr, ""
        
    def test_default(self):
        """Test view parser"""
        args = parse_args(shlex.split('view file.sff'))
        
        self.assertEqual(args.from_file, 'file.sff')
        self.assertFalse(args.version)
    
    def test_version(self):
        """Test view version"""
        args = parse_args(shlex.split('view -V file.sff'))
        
        self.assertTrue(args.version)


class TestParser_notes_ro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print >> sys.stderr, "notes ro tests..."
        
    @classmethod
    def tearDownClass(cls):
        print >> sys.stderr, ""
        
    #=========================================================================
    # find
    #=========================================================================
    def test_search_default(self):
        """Test default find parameters"""
        args = parse_args(shlex.split("notes search 'mitochondria'"))
        self.assertEqual(args.notes_subcommand, 'search')
        self.assertEqual(args.search_term, 'mitochondria')
        self.assertEqual(args.rows, 10)
        self.assertEqual(args.start, 1)
        self.assertIsNone(args.ontology)
        self.assertFalse(args.exact)
        self.assertFalse(args.obsoletes)
        self.assertFalse(args.list_ontologies)
        self.assertFalse(args.short_list_ontologies)
        
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
        args = parse_args(shlex.split("notes search -r {} -s {} -O fma -x -o -L -l 'mitochondria'".format(rows, start)))
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
        start = - _random_integer()
        with self.assertRaises(ValueError):
            parse_args(shlex.split("notes search -s {} 'mitochondria'".format(start)))
    
    def test_search_invalid_rows(self):
        """Test that we catch an invalid rows"""
        rows = - _random_integer()
        with self.assertRaises(ValueError):
            parse_args(shlex.split("notes search -r {} 'mitochondria'".format(rows)))
        
    #=========================================================================
    # view
    #=========================================================================
    def test_list_default(self):
        """Test that we can list notes from an SFF file"""
        args = parse_args(shlex.split('notes list file.sff'))
        # assertion
        self.assertEqual(args.notes_subcommand, 'list')
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertFalse(args.long_format)
        self.assertFalse(args.sort_by_description)
        self.assertFalse(args.reverse)
        
    def test_list_long(self):
        """Test short list of notes"""
        args = parse_args(shlex.split('notes list -l file.sff'))
        # assertions
        self.assertTrue(args.long_format)
        
    def test_list_shortcut(self):
        """Test that shortcut fails with list"""
        args = parse_args(shlex.split('notes list @'))
        # assertions
        self.assertIsNone(args)
        
    def test_list_sort_by_description(self):
        """Test list segments sorted by description"""
        args = parse_args(shlex.split('notes list -D file.sff'))
        # assertions
        self.assertTrue(args.sort_by_description)
        
    def test_list_reverse_sort(self):
        """Test list sort in reverse"""
        args = parse_args(shlex.split('notes list -r file.sff'))
        # assertions
        self.assertTrue(args.reverse)
        
    def test_show_default(self):
        """Test show notes"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args = parse_args(shlex.split('notes show -i {},{} file.sff'.format(segment_id0, segment_id1)))
        # assertions
        self.assertEqual(args.notes_subcommand, 'show')
        self.assertItemsEqual(args.segment_id, [segment_id0, segment_id1])
        self.assertEqual(args.sff_file, 'file.sff')
        self.assertFalse(args.long_format)
        
    def test_show_short(self):
        """Test short show of notes"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args = parse_args(shlex.split('notes show -l -i {},{} file.sff'.format(segment_id0, segment_id1)))
        # assertions 
        self.assertTrue(args.long_format)
        
    def test_show_shortcut(self):
        """Test that shortcut works with show"""
        segment_id0 = _random_integer()
        segment_id1 = _random_integer()
        args = parse_args(shlex.split('notes show -i {},{} @'.format(segment_id0, segment_id1)))
        # assertions
        self.assertIsNone(args)

 
class TestParser_notes_rw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print >> sys.stderr, "notes rw tests..."
        
    @classmethod
    def tearDownClass(cls):
        print >> sys.stderr, ""
        
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.temp_file = configs['__TEMP_FILE']
        if os.path.exists(self.temp_file):
            raise ValueError("Unable to run with temp file {} present. \
Please either run 'save' or 'trash' before running tests.".format(self.temp_file))
              
    def tearDown(self):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            assert not os.path.exists(self.temp_file)
        unittest.TestCase.tearDown(self)
        
    #===========================================================================
    # notes: add
    #===========================================================================
    def test_add_default(self):
        """Test add notes"""
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        args = parse_args(shlex.split('notes add -i {} -D something -n {} -E abc ABC -C xyz,XYZ -M opq,OPQ file.sff'.format(segment_id, number_of_instances)))
        # assertions
        self.assertEqual(args.notes_subcommand, 'add')
        self.assertItemsEqual(args.segment_id, [segment_id])
        self.assertEqual(args.description, 'something')
        self.assertEqual(args.number_of_instances, number_of_instances)
        self.assertItemsEqual(args.external_ref, [['abc', 'ABC']])
        self.assertItemsEqual(args.complexes, ['xyz', 'XYZ'])
        self.assertItemsEqual(args.macromolecules, ['opq', 'OPQ'])
        self.assertEqual(args.sff_file, 'file.sff')
        
    def test_add_addendum_missing(self):
        """Test assertion fails if addendum is missing"""
        segment_id = _random_integer()
        args = parse_args(shlex.split('notes add -i {} file.sff'.format(segment_id)))
        self.assertEqual(args, None)
        
    #===========================================================================
    # notes: edit
    #===========================================================================
    def test_edit_default(self):
        """Test edit notes"""
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        external_ref_id = _random_integer()
        complex_id = _random_integer()
        macromolecule_id = _random_integer()
        args = parse_args(shlex.split('notes edit -i {} -D something -n {} -e {} -E abc ABC -c {} -C xyz -m {} -M opq file.sff'.format(
            segment_id, number_of_instances, external_ref_id, complex_id, macromolecule_id,
            )))
           
        self.assertEqual(args.notes_subcommand, 'edit')
        self.assertItemsEqual(args.segment_id, [segment_id])
        self.assertEqual(args.description, 'something')
        self.assertEqual(args.number_of_instances, number_of_instances)
        self.assertEqual(args.external_ref_id, external_ref_id)
        self.assertItemsEqual(args.external_ref, [['abc', 'ABC']])
        self.assertEqual(args.complex_id, complex_id)
        self.assertItemsEqual(args.complexes, ['xyz'])
        self.assertEqual(args.macromolecule_id, macromolecule_id)
        self.assertItemsEqual(args.macromolecules, ['opq'])
        self.assertEqual(args.sff_file, 'file.sff')
    def test_edit_failure_on_missing_ids(self):
        """Test handling of missing IDs"""
        segment_id = _random_integer()
        number_of_instances = _random_integer()
        external_ref_id = _random_integer()
        complex_id = _random_integer()
        macromolecule_id = _random_integer()
        args = parse_args(shlex.split('notes edit -i {} -D something -n {} -E abc ABC -c {} -C xyz -m {} -M opq file.sff'.format(
            segment_id, number_of_instances, complex_id, macromolecule_id,
            )))
      
        self.assertIsNone(args)
          
        args1 = parse_args(shlex.split('notes edit -i {} -D something -n {} -e {} -E abc ABC -C xyz -m {} -M opq @'.format(
            segment_id, number_of_instances, external_ref_id, macromolecule_id,
            )))
      
        self.assertIsNone(args1)
          
        args2 = parse_args(shlex.split('notes edit -i {} -D something -n {} -e {} -E abc ABC -c {} -C xyz -M opq @'.format(
            segment_id, number_of_instances, external_ref_id, complex_id,
            )))
      
        self.assertIsNone(args2)
    #===========================================================================
    # notes: del
    #===========================================================================
    def test_del_default(self):
        """Test del notes"""
        segment_id = _random_integer()
        external_ref_id = _random_integer()
        complex_id = _random_integer()
        macromolecule_id = _random_integer()
        args = parse_args(shlex.split('notes del -i {} -D -n -e {} -c {} -m {} file.sff'.format(
            segment_id, external_ref_id, complex_id, macromolecule_id,
            )))
          
        self.assertEqual(args.notes_subcommand, 'del')
        self.assertItemsEqual(args.segment_id, [segment_id])
        self.assertTrue(args.description)
        self.assertTrue(args.number_of_instances)
        self.assertEqual(args.external_ref_id, external_ref_id)
        self.assertEqual(args.complex_id, complex_id)
        self.assertEqual(args.macromolecule_id, macromolecule_id)
        self.assertEqual(args.sff_file, 'file.sff')
    #=========================================================================
    # notes: save
    #=========================================================================
    def test_save(self):
        """Test save edits"""
        segment_id = _random_integer()
        args = parse_args(shlex.split("notes edit -i {} -D something file.sff".format(segment_id)))
        self.assertEqual(args.sff_file, 'file.sff')
        # can only save to an existing file
        save_fn = os.path.join(TEST_DATA_PATH, 'sff', 'emd_1014.sff')
        args1 = parse_args(shlex.split("notes save {}".format(save_fn)))
        self.assertEqual(args1.notes_subcommand, 'save')
        self.assertEqual(args1.sff_file, save_fn)
    #===========================================================================
    # notes: trash
    #===========================================================================
    def test_trash(self):
        """Test trash notes"""
        segment_id = _random_integer()
        args = parse_args(shlex.split("notes edit -i {} -D something file.sff".format(segment_id)))
        self.assertEqual(args.sff_file, 'file.sff')
        args1 = parse_args(shlex.split("notes trash @"))
        self.assertEqual(args1.notes_subcommand, 'trash')
