#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for :py:mod:`sfftk.core.notes` package"""

from __future__ import division, print_function

import os
import shutil
import sys
import unittest

from random_words import RandomWords, LoremIpsum

from . import TEST_DATA_PATH, _random_integer, Py23FixTestCase, _random_integers
from .. import BASE_DIR
from .. import schema
from ..core import _urlencode, _xrange, _str
from ..core import utils
from ..core.parser import parse_args
from ..notes import find, modify, view, RESOURCE_LIST
from ..sff import _handle_notes_modify, handle_notes_trash

rw = RandomWords()
li = LoremIpsum()

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-05-15"


# :TODO: rewrite to use sfftk.notes.modify.SimpleNote


class TestNotesModifyExternalReference(Py23FixTestCase):
    def test_ols(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        type_ = u'ncit'
        otherType = u'http://purl.obolibrary.org/obo/NCIT_C62195'
        value = u'NCIT_C62195'
        # likely to change
        label = u'Wild Type'
        description = u'The naturally-occurring, normal, non-mutated version of a gene or genome.'
        urlenc = _urlencode({u'iri': otherType.encode(u'idna')})
        urlenc2 = _urlencode({u'iri': urlenc.split(u'=')[1]})
        urlenc3 = urlenc2.split(u'=')[1]
        extRef = modify.ExternalReference(
            type_=type_,
            otherType=otherType,
            value=value,
        )
        self.assertEqual(extRef.type, type_)
        self.assertEqual(extRef.otherType, otherType)
        self.assertEqual(extRef.value, value)
        self.assertEqual(extRef.label, label)
        self.assertEqual(extRef.description,
                         description)
        self.assertCountEqual(extRef._get_text(), [label, description])
        self.assertEqual(extRef.iri, urlenc3)

    def test_emdb(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        type_ = u'EMDB'
        otherType = u'https://www.ebi.ac.uk/pdbe/emdb/EMD-8654'
        value = u'EMD-8654'
        # likely to change
        label = u'EMD-8654'
        description = u'Zika virus-infected Vero E6 cell at 48 hpi: dual-axis tilt series tomogram from 3 serial sections'
        extRef = modify.ExternalReference(
            type_=type_,
            otherType=otherType,
            value=value,
        )
        self.assertEqual(extRef.type, type_)
        self.assertEqual(extRef.otherType, otherType)
        self.assertEqual(extRef.value, value)
        self.assertEqual(extRef.label, label)
        self.assertEqual(extRef.description,
                         description)
        self.assertCountEqual(extRef._get_text(), [label, description])

    def test_pdb(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        type_ = u'PDB'
        otherType = u'https://www.ebi.ac.uk/pdbe/entry/pdb/4gzw'
        value = u'4gzw'
        # likely to change
        label = u'N2 neuraminidase D151G mutant of A/Tanzania/205/2010 H3N2 in complex with avian sialic acid receptor'
        description = u'H3N2 subtype'
        extRef = modify.ExternalReference(
            type_=type_,
            otherType=otherType,
            value=value,
        )
        self.assertEqual(extRef.type, type_)
        self.assertEqual(extRef.otherType, otherType)
        self.assertEqual(extRef.value, value)
        self.assertEqual(extRef.label, label)
        self.assertEqual(extRef.description,
                         description)
        self.assertCountEqual(extRef._get_text(), [label, description])

    def test_uniprot(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        type_ = u'UniProt'
        otherType = u'https://www.uniprot.org/uniprot/A0A1Q8WSX6'
        value = u'A0A1Q8WSX6'
        # likely to change
        label = u'A0A1Q8WSX6_9ACTO'
        description = u'Type I-E CRISPR-associated protein Cas5/CasD (Organism: Actinomyces oris)'
        extRef = modify.ExternalReference(
            type_=type_,
            otherType=otherType,
            value=value,
        )
        self.assertEqual(extRef.type, type_)
        self.assertEqual(extRef.otherType, otherType)
        self.assertEqual(extRef.value, value)
        self.assertEqual(extRef.label, label)
        self.assertEqual(extRef.description,
                         description)
        self.assertCountEqual(extRef._get_text(), [label, description])

    def test_europepmc(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        type_ = u'Europe PMC'
        otherType = u'http://europepmc.org/abstract/MED/30932919'
        value = u'30932919'
        label = u'Perugi G, De Rossi P, Fagiolini A, Girardi P, Maina G, Sani G, Serretti A.'
        description = u'Personalized and precision medicine as informants for treatment management of bipolar disorder.'
        extRef = modify.ExternalReference(
            type_=type_,
            otherType=otherType,
            value=value,
        )
        self.assertEqual(extRef.type, type_)
        self.assertEqual(extRef.otherType, otherType)
        self.assertEqual(extRef.value, value)
        self.assertEqual(extRef.label, label)
        self.assertEqual(extRef.description,
                         description)
        self.assertCountEqual(extRef._get_text(), [label, description])

    def test_empiar(self):
        """Test that sfftk.notes.modify.ExternalReference object works correctly"""
        type_ = u'EMPIAR'
        otherType = u'https://www.ebi.ac.uk/pdbe/emdb/empiar/entry/10087/'
        value = u'EMPIAR-10087'
        label = u'Soft X-ray tomography of Plasmodium falciparum infected human erythrocytes stalled in egress by the ' \
                u'inhibitors Compound 2 and E64'
        description = u'SXT'
        extRef = modify.ExternalReference(
            type_=type_,
            otherType=otherType,
            value=value,
        )
        self.assertEqual(extRef.type, type_)
        self.assertEqual(extRef.otherType, otherType)
        self.assertEqual(extRef.value, value)
        self.assertEqual(extRef.label, label)
        self.assertEqual(extRef.description,
                         description)
        self.assertCountEqual(extRef._get_text(), [label, description])


class TestNotesFindSearchResource(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_unknown_resource(self):
        """Test exception raised formed unknown resource"""
        with self.assertRaises(SystemExit):
            args, config = parse_args(
                'notes search --resource xxx "something" --config-path {}'.format(self.config_fn),
                use_shlex=True
            )

    def test_configs_attribute(self):
        """Test the value of the configs attribute"""
        args, configs = parse_args(
            'notes search --resource ols "mitochondria" --config-path {}'.format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.configs, configs)

    def test_result_path(self):
        """Test result path attr"""
        args, configs = parse_args("notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn),
                                   use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.result_path, RESOURCE_LIST['ols']['result_path'])

    def test_result_count(self):
        """Test result_count attr"""
        args, configs = parse_args(
            "notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.result_count, RESOURCE_LIST['ols']['result_count'])

    def test_format(self):
        """Test format attr"""
        args, configs = parse_args("notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn),
                                   use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertEqual(resource.format, RESOURCE_LIST['ols']['format'])

    def test_response(self):
        """Test response attr"""
        args, configs = parse_args(
            "notes search -R ols 'mitochondria' --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        self.assertIsNone(resource.response)
        resource.search()
        url = resource.get_url()
        # print('url: ' + url, file=sys.stderr)
        import requests
        import json
        R = requests.get(url)
        resource_results = utils.get_path(json.loads(resource.response), resource.result_path)
        test_results = utils.get_path(json.loads(R.text), resource.result_path)
        self.assertCountEqual(resource_results, test_results)

    def test_get_url_ols_list_ontologies(self):
        """Test url correctness for OLS"""
        resource_name = 'ols'
        args, configs = parse_args("notes search -R {resource_name} 'mitochondria' -L --config-path {config_fn}".format(
            resource_name=resource_name,
            config_fn=self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}ontologies?size=1000".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_ols(self):
        """Test url correctness for OLS"""
        resource_name = 'ols'
        args, configs = parse_args(
            "notes search -R {resource_name} 'mitochondria' -O go -x -o --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}search?q={search_term}&start={start}&rows={rows}&local=true&ontology={ontology}&exact=on&obsoletes=on".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start - 1,
            rows=args.rows,
            ontology=args.ontology,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_emdb(self):
        """Test url correctness for EMDB"""
        resource_name = 'emdb'
        args, configs = parse_args("notes search -R {resource_name} 'mitochondria' --config-path {config_fn}".format(
            resource_name=resource_name,
            config_fn=self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}?q={search_term}&start={start}&rows={rows}".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_uniprot(self):
        """Test url correctness for UniProt"""
        resource_name = 'uniprot'
        args, configs = parse_args(
            "notes search -R {resource_name} 'mitochondria' --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}?query={search_term}&format=tab&offset={start}&limit={rows}&columns=id,entry_name,protein_names,organism".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_pdb(self):
        """Test url correctness for PDB"""
        resource_name = 'pdb'
        args, configs = parse_args("notes search -R {resource_name} 'mitochondria' --config-path {config_fn}".format(
            resource_name=resource_name,
            config_fn=self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        url = "{root_url}?q={search_term}&wt=json&fl=pdb_id,title,organism_scientific_name&start={start}&rows={rows}".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_europepmc(self):
        """Test url correctness for Europe PMC"""
        resource_name = 'europepmc'
        args, configs = parse_args(
            "notes search -R {resource_name} 'picked' --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ), use_shlex=True
        )
        resource = find.SearchResource(args, configs)
        url = "{root_url}search?query={search_term}&resultType=lite&cursorMark=*&pageSize={rows}&format=json".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            rows=args.rows,
        )
        self.assertEqual(resource.get_url(), url)

    def test_get_url_empiar(self):
        """Test url correctness for EMPIAR"""
        resource_name = 'empiar'
        args, configs = parse_args(
            "notes search -R {resource_name} 'picked' --config-path {config_fn}".format(
                resource_name=resource_name,
                config_fn=self.config_fn,
            ),
            use_shlex=True,
        )
        resource = find.SearchResource(args, configs)
        url = "{root_url}?q={search_term}&wt=json&start={start}&rows={rows}".format(
            root_url=RESOURCE_LIST[resource_name]['root_url'],
            search_term=args.search_term,
            start=args.start,
            rows=args.rows
        )
        # the url has an additional random (unpredictable) value that will break the comparison
        # let's remove it before the equality assertion
        resource_url = '&'.join(resource.get_url().split('&')[:-1])
        self.assertEqual(resource_url, url)


# class TestNotesFindSearchResource(Py23FixTestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
#
#     def test_search_args_attr(self):
#         """Test that search_args attr works"""
#         args, configs = parse_args(
#             "notes search -R emdb mitochondria --config-path {}".format(self.config_fn), use_shlex=True)
#         resource = find.SearchResource(args, configs)
#         self.assertEqual(resource.search_args, args)


class TestNotesFindTableField(Py23FixTestCase):
    def test_init_name(self):
        """Test instantiation of TableField object"""
        with self.assertRaisesRegexp(ValueError,
                                     "key and text are mutually exclusive; only define one or none of them"):
            find.TableField('my-field', key='k', text='t')

    def test_init_width_type(self):
        """Test check on width type"""
        with self.assertRaisesRegexp(ValueError, "field width must be int or long"):
            find.TableField('my-field', width=1.3)

    def test_init_width_value(self):
        """Test check on width value"""
        with self.assertRaisesRegexp(ValueError, "field width must be greater than 0"):
            find.TableField('my-field', width=0)

    def test_init_pc_type(self):
        """Test pc type"""
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc='1.3')
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=u'1.3')
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=list())
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=dict())
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=tuple())

    def test_init_pc_value(self):
        """Test pc value"""
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=-1)
        with self.assertRaises(ValueError):
            find.TableField('my-field', pc=100)
        self.assertIsInstance(find.TableField('my-field', pc=50), find.TableField)

    def test_init_justify(self):
        """Test value for justify"""
        self.assertIsInstance(find.TableField('my-field', text='t', justify='left'), find.TableField)
        self.assertIsInstance(find.TableField('my-field', text='t', justify='right'), find.TableField)
        self.assertIsInstance(find.TableField('my-field', text='t', justify='center'), find.TableField)


class TestNotes_view(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def setUp(self):
        self.segment_id = 15559
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.sff')

    def test_list_default(self):
        """Test that we can view the list of segmentations with annotations"""
        args, configs = parse_args("notes list {} --config-path {}".format(
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.list_notes(args, configs)
        # assertions
        self.assertEqual(status, 0)

    def test_long_list(self):
        """Test that we can long list (-l) the list of segmentations with annotations"""
        args, configs = parse_args("notes list -l {} --config-path {}".format(
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.list_notes(args, configs)
        # assertions
        self.assertEqual(status, 0)

    def test_show_default(self):
        """Test that we can show annotations in a single segment"""
        args, configs = parse_args("notes show -i {} {} --config-path {}".format(
            self.segment_id,
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.show_notes(args, configs)
        self.assertEqual(status, 0)

    def test_long_show(self):
        """Test that we can show in long format annotations in a single segment"""
        args, configs = parse_args("notes show -l -i {} {} --config-path {}".format(
            self.segment_id,
            self.sff_file,
            self.config_fn,
        ), use_shlex=True)
        status = view.show_notes(args, configs)
        self.assertEqual(status, 0)


class TestNotes_modify(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')
        cls.sff_file = None
        cls.output = None
        cls.annotated_sff_file = None

    # test filetypeA to filetypeB
    def setUp(self):
        # remove any temporary files
        args, configs = parse_args("notes trash @ --config-path {config}".format(
            config=self.config_fn), use_shlex=True
        )
        handle_notes_trash(args, configs)
        self.segment_id = 15559

    def tearDown(self):
        # remove any temporary files
        args, configs = parse_args("notes trash @ --config-path {config}".format(
            config=self.config_fn), use_shlex=True
        )
        handle_notes_trash(args, configs)

    def _test_add(self):
        """Test that we can add a note"""
        segment_name = 'the segment name'
        desc = 'a short description'
        num = _random_integer()
        extref = ['lsfj', 'sljfs', 'ldjls']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        cmd = "notes add -i {segment_id} -s '{name}' -d '{description}' -E {extref} -n {num} -C {complexes} " \
              "-M {macromolecules} {sff_file} --config-path {config}".format(
            segment_id=self.segment_id,
            name=segment_name,
            description=desc,
            extref=" ".join(extref),
            num=num,
            complexes=','.join(complexes),
            macromolecules=','.join(macromolecules),
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        # first we get the raw args
        _args, configs = parse_args(cmd, use_shlex=True)
        # we intercept them for 'modify' actions
        args = _handle_notes_modify(_args, configs)
        # we pass modified args for 'temp-annotated.json'
        status = modify.add_note(args, configs)
        seg = schema.SFFSegmentation(args.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status, 0)
        self.assertEqual(segment.biologicalAnnotation.description, desc)
        self.assertEqual(segment.biologicalAnnotation.numberOfInstances, num)
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].type, extref[0])
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].otherType, extref[1])
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].value, extref[2])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[0], complexes[0])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[1], complexes[1])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[2], complexes[2])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[0], macromolecules[0])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[1], macromolecules[1])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[2], macromolecules[2])

    def _test_edit(self):
        """Test that we can edit a note"""
        segment_name = "the segments name"
        desc = 'a short description'
        num = _random_integer()
        extref = ['lsfj', 'sljfs', 'ldjss']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        # add
        cmd = "notes add -i {segment_id} -s '{name}' -D '{desc}' -E {extref} -n {num} -C {complexes} " \
              "-M {macromolecules} {sff_file} --config-path {config}".format(
            segment_id=self.segment_id,
            name=segment_name,
            desc=desc,
            extref=" ".join(extref),
            num=num,
            complexes=','.join(complexes),
            macromolecules=','.join(macromolecules),
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        modify.add_note(args, configs)
        segment_name1 = segment_name[::-1]
        desc1 = desc[::-1]
        num1 = _random_integer()
        extref1 = list(map(lambda e: e[::-1], extref))
        cmd1 = "notes edit -i {segment_id} -s '{name}' -d '{description}' " \
               "-e 0 -E {extref} -n {num} -c 1 -C {complexes} -m 2 -M {macromolecules} " \
               "@ --config-path {config}".format(
            segment_id=self.segment_id,
            name=segment_name1,
            description=desc1,
            extref=" ".join(extref1),
            num=num1,
            complexes=complexes[1][::-1],
            macromolecules=macromolecules[2][::-1],
            config=self.config_fn,
        )
        _args1, configs = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs)
        # edit
        status1 = modify.edit_note(args1, configs)
        # we have to compare against the temp-annotated.json file!!!
        seg = schema.SFFSegmentation(args1.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status1, 0)
        self.assertEqual(segment.biologicalAnnotation.name, segment_name1)
        self.assertEqual(segment.biologicalAnnotation.description, desc1)
        self.assertEqual(segment.biologicalAnnotation.numberOfInstances, num1)
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].type, extref1[0])
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].otherType, extref1[1])
        self.assertEqual(segment.biologicalAnnotation.externalReferences[0].value, extref1[2])
        self.assertEqual(segment.complexesAndMacromolecules.complexes[1], complexes[1][::-1])
        self.assertEqual(segment.complexesAndMacromolecules.macromolecules[2], macromolecules[2][::-1])

    def _test_del(self):
        """Test that we can delete a note"""
        segment_name = 'the segment name'
        desc = 'a short description'
        num = _random_integer()
        extref = ['lsfj', 'sljfs', 'dsljfl']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        cmd = "notes add -i {segment_id} -D '{description}' -E {extref} -n {num} -C {complexes} -M {macromolecules} " \
              "{sff_file} --config-path {config}".format(
            segment_id=self.segment_id,
            description=desc,
            extref=" ".join(extref),
            num=num,
            complexes=','.join(complexes),
            macromolecules=','.join(macromolecules),
            sff_file=self.sff_file,
            config=self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        # add
        modify.add_note(args, configs)
        # delete
        cmd1 = "notes del -i {segment_id} -D -e 0 -n -c 0 -m 1 @ --config-path {config}".format(
            segment_id=self.segment_id,
            config=self.config_fn,
        )
        _args1, configs = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs)
        status1 = modify.del_note(args1, configs)
        seg = schema.SFFSegmentation(args1.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(status1, 0)
        self.assertIsNone(segment.biologicalAnnotation.name)
        self.assertIsNone(segment.biologicalAnnotation.description)
        self.assertIsNone(segment.biologicalAnnotation.numberOfInstances)
        self.assertEqual(len(segment.biologicalAnnotation.externalReferences), 0)
        self.assertEqual(len(segment.complexesAndMacromolecules.complexes), 2)
        self.assertEqual(len(segment.complexesAndMacromolecules.macromolecules), 2)

    def _test_merge(self):
        """Test that we can merge notes"""
        segment_name = 'my very nice segment'
        desc = 'a short description'
        num = _random_integer()
        extref = ['lsfj', 'sljfs', 'ldjss']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        # add
        cmd = "notes add -i {} -s '{}' -d '{}' -E {} -n {} -C {} -M {} {} --config-path {}".format(
            self.segment_id,
            segment_name,
            desc,
            " ".join(extref),
            num,
            ','.join(complexes),
            ','.join(macromolecules),
            self.sff_file,
            self.config_fn,
        )
        args, configs = parse_args(cmd, use_shlex=True)
        status = modify.add_note(args, configs)
        self.assertEqual(status, 0)
        # merge
        cmd1 = 'notes merge --source {source} {other} --output {output} --config-path {config_fn}'.format(
            source=self.sff_file,
            other=self.other,
            output=self.output,
            config_fn=self.config_fn,
        )
        args1, configs1 = parse_args(cmd1, use_shlex=True)
        status1 = modify.merge(args1, configs1)
        self.assertEqual(status1, 0)
        source_seg = schema.SFFSegmentation(self.sff_file)
        output_seg = schema.SFFSegmentation(self.output)
        source_segment = source_seg.segments.get_by_id(self.segment_id)
        # print('description: ' + source_segment.biologicalAnnotation.description, file=sys.stderr)
        output_segment = output_seg.segments.get_by_id(self.segment_id)
        self.assertEqual(source_segment.biologicalAnnotation.name, segment_name)
        self.assertEqual(source_segment.biologicalAnnotation.description, desc)
        self.assertEqual(source_segment.biologicalAnnotation.description,
                         output_segment.biologicalAnnotation.description)
        self.assertEqual(source_segment.biologicalAnnotation.numberOfInstances, num)
        self.assertEqual(source_segment.biologicalAnnotation.numberOfInstances,
                         output_segment.biologicalAnnotation.numberOfInstances)
        self.assertEqual(source_segment.biologicalAnnotation.externalReferences[0].type, extref[0])
        self.assertEqual(source_segment.biologicalAnnotation.externalReferences[0].otherType, extref[1])
        self.assertEqual(source_segment.biologicalAnnotation.externalReferences[0].value, extref[2])
        self.assertEqual(source_segment.biologicalAnnotation.externalReferences[0].type,
                         output_segment.biologicalAnnotation.externalReferences[0].type)
        self.assertEqual(source_segment.complexesAndMacromolecules.complexes[0], complexes[0])
        self.assertEqual(source_segment.complexesAndMacromolecules.complexes[1], complexes[1])
        self.assertEqual(source_segment.complexesAndMacromolecules.complexes[2], complexes[2])
        self.assertEqual(source_segment.complexesAndMacromolecules.macromolecules[0], macromolecules[0])
        self.assertEqual(source_segment.complexesAndMacromolecules.macromolecules[1], macromolecules[1])
        self.assertEqual(source_segment.complexesAndMacromolecules.macromolecules[2], macromolecules[2])
        self.assertEqual(source_segment.complexesAndMacromolecules.complexes[0],
                         output_segment.complexesAndMacromolecules.complexes[0])
        self.assertEqual(source_segment.complexesAndMacromolecules.complexes[1],
                         output_segment.complexesAndMacromolecules.complexes[1])
        self.assertEqual(source_segment.complexesAndMacromolecules.complexes[2],
                         output_segment.complexesAndMacromolecules.complexes[2])
        self.assertEqual(source_segment.complexesAndMacromolecules.macromolecules[0],
                         output_segment.complexesAndMacromolecules.macromolecules[0])
        self.assertEqual(source_segment.complexesAndMacromolecules.macromolecules[1],
                         output_segment.complexesAndMacromolecules.macromolecules[1])
        self.assertEqual(source_segment.complexesAndMacromolecules.macromolecules[2],
                         output_segment.complexesAndMacromolecules.macromolecules[2])

    def _test_clear(self):
        """Test that we can clear notes"""
        segment_name = 'my very nice segment'
        desc = 'a short description'
        num = _random_integer()
        extref = ['lsfj', 'sljfs', 'ldjss']
        complexes = ['09ej', 'euoisd', 'busdif']
        macromolecules = ['xuidh', '29hf98e', 'ygce']
        # add
        cmd = "notes add -i {} -s '{}' -D '{}' -E {} -n {} -C {} -M {} {} --config-path {}".format(
            self.segment_id,
            segment_name,
            desc,
            " ".join(extref),
            num,
            ','.join(complexes),
            ','.join(macromolecules),
            self.sff_file,
            self.config_fn,
        )
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        status = modify.add_note(args, configs)
        self.assertEqual(status, 0)
        # clear
        cmd1 = 'notes clear --all @ --config-path {config_fn}'.format(
            # self.sff_file,
            config_fn=self.config_fn,
        )
        _args1, configs1 = parse_args(cmd1, use_shlex=True)
        args1 = _handle_notes_modify(_args1, configs1)
        status1 = modify.clear_notes(args1, configs1)
        self.assertEqual(status1, 0)
        seg = schema.SFFSegmentation(args1.sff_file)
        segment = seg.segments.get_by_id(self.segment_id)
        self.assertEqual(len(segment.biologicalAnnotation.externalReferences), 0)

    def _test_copy(self):
        """Test that we can copy notes"""
        # we have an annotated EMDB-SFF file
        # make a copy of the file for the test
        annotated_sff_file = os.path.join(os.path.dirname(self.annotated_sff_file),
                                          'temp_' + os.path.basename(self.annotated_sff_file))
        shutil.copy2(self.annotated_sff_file, annotated_sff_file)
        # use the file copy
        # before copy
        seg = schema.SFFSegmentation(annotated_sff_file)
        source_segment = seg.segments.get_by_id(15559)
        # copy
        cmd = "notes copy -i 15559 -t 15578 {ann_sff_file} --config-path {config}".format(
            ann_sff_file=annotated_sff_file,
            config=self.config_fn
        )
        print(cmd, file=sys.stderr)
        _args, configs = parse_args(cmd, use_shlex=True)
        args = _handle_notes_modify(_args, configs)
        status1 = modify.copy_notes(args, configs)
        # save
        cmd1 = "notes save {sff_file} --config-path {config}".format(
            sff_file=annotated_sff_file,
            config=self.config_fn,
        )
        print(cmd1, file=sys.stderr)
        args, configs = parse_args(cmd1, use_shlex=True)
        status3 = modify.save(args, configs)
        # debug
        cmd2 = "notes list {sff_file} --config-path {config}".format(
            sff_file=annotated_sff_file,
            config=self.config_fn
        )
        _args1, config = parse_args(cmd2, use_shlex=True)
        args1 = _handle_notes_modify(_args1, config)
        view.list_notes(args1, config)
        self.assertEqual(status1, 0)

        copied_seg = schema.SFFSegmentation(annotated_sff_file)
        copied_segment = copied_seg.segments.get_by_id(15578)
        self.assertEqual(len(source_segment.biologicalAnnotation.externalReferences),
                         len(copied_segment.biologicalAnnotation.externalReferences))
        self.assertEqual(source_segment.biologicalAnnotation.externalReferences[0].type,
                         copied_segment.biologicalAnnotation.externalReferences[0].type)
        self.assertEqual(source_segment.biologicalAnnotation.externalReferences[0].otherType,
                         copied_segment.biologicalAnnotation.externalReferences[0].otherType)
        self.assertEqual(source_segment.biologicalAnnotation.externalReferences[0].value,
                         copied_segment.biologicalAnnotation.externalReferences[0].value)
        # # get rid of the copy
        os.remove(annotated_sff_file)


class TestNotes_modify_sff(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_sff, self).setUp()
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.sff')
        self.other = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'other_emd_1014.sff')
        self.output = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'output_emd_1181.sff')
        self.annotated_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'annotated_emd_1014.sff')

    def tearDown(self):
        super(TestNotes_modify_sff, self).tearDown()
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

    def test_merge(self):
        super(TestNotes_modify_sff, self)._test_merge()

    def test_clear(self):
        super(TestNotes_modify_sff, self)._test_clear()

    def test_copy(self):
        super(TestNotes_modify_sff, self)._test_copy()


class TestNotes_modify_hff(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_hff, self).setUp()
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.hff')
        self.other = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'other_emd_1014.hff')
        self.output = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'output_emd_1014.hff')
        self.annotated_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'annotated_emd_1014.hff')

    def tearDown(self):
        super(TestNotes_modify_hff, self).tearDown()
        seg = schema.SFFSegmentation(self.sff_file)
        # remove all annotations
        for segment in seg.segments:
            segment.biologicalAnnotation = schema.SFFBiologicalAnnotation()
            segment.complexesAndMacromolecules = schema.SFFComplexesAndMacromolecules()
        seg.export(self.sff_file)

    def test_add(self):
        super(TestNotes_modify_hff, self)._test_add()

    def test_edit(self):
        super(TestNotes_modify_hff, self)._test_edit()

    def test_del(self):
        super(TestNotes_modify_hff, self)._test_del()

    def test_clear(self):
        super(TestNotes_modify_hff, self)._test_clear()

    # fixme: can't figure out why this fails
    def test_copy(self):
        super(TestNotes_modify_hff, self)._test_copy()


class TestNotes_modify_json(TestNotes_modify):
    def setUp(self):
        super(TestNotes_modify_json, self).setUp()
        self.sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'emd_1014.json')
        self.other = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'other_emd_1014.json')
        self.output = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'output_emd_1181.json')
        self.annotated_sff_file = os.path.join(TEST_DATA_PATH, 'sff', 'v0.7', 'annotated_emd_1014.json')

    def tearDown(self):
        super(TestNotes_modify_json, self).tearDown()
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

    def test_merge(self):
        super(TestNotes_modify_json, self)._test_merge()

    def test_clear(self):
        super(TestNotes_modify_json, self)._test_clear()

    def test_copy(self):
        super(TestNotes_modify_json, self)._test_copy()


class TestNotesClasses(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_SimpleNote(self):
        """Test SimpleNote class"""
        name = li.get_sentence()
        description = li.get_sentences(5)
        num = _random_integer(1)
        numExtRefs = _random_integer(2)
        extRefs = [rw.random_words(count=3) for _ in _xrange(3)]
        complexId = _random_integer(1)
        complexes = rw.random_words(count=_random_integer(2, 7))
        macromoleculeId = _random_integer(1)
        macromolecules = rw.random_words(count=_random_integer(2, 7))
        sn = modify.SimpleNote(
            name=name,
            description=description,
            numberOfInstances=num,
            externalReferenceId=numExtRefs,
            externalReferences=extRefs,
            complexId=complexId,
            complexes=complexes,
            macromoleculeId=macromoleculeId,
            macromolecules=macromolecules,
        )
        self.assertEqual(sn.name, name)
        self.assertEqual(sn.description, description)
        self.assertEqual(sn.numberOfInstances, num)
        self.assertEqual(sn.complexId, complexId)
        self.assertEqual(sn.macromoleculeId, macromoleculeId)
        for idx, extRef_ in enumerate(sn.externalReferences):
            self.assertCountEqual(
                [extRef_.type, extRef_.otherType, extRef_.value],
                extRefs[idx],
            )
            self.assertIsInstance(extRef_, modify.ExternalReference)
        self.assertCountEqual(sn.complexes, complexes)
        self.assertCountEqual(sn.macromolecules, macromolecules)
        # direct assigment of external references
        eRefs = [rw.random_words(count=3) for _ in _xrange(3)]
        sn.externalReferences = eRefs
        for idx, extRef_ in enumerate(sn.externalReferences):
            self.assertCountEqual(
                [extRef_.type, extRef_.otherType, extRef_.value],
                eRefs[idx],
            )
            self.assertIsInstance(extRef_, modify.ExternalReference)

    def test_GlobalArgsNote(self):
        """Test GlobalArgsNote (construct global notes from command-line arguments)"""
        name = li.get_sentence()
        details = li.get_sentences(sentences=10)
        sw_name = rw.random_word()
        sw_version = rw.random_word()
        sw_proc = li.get_sentences(sentences=5)
        extRefs = [rw.random_words(count=3) for _ in _xrange(3)]
        cmd = "notes add -N '{name}' -D '{details}' -S '{sw_name}' -V '{sw_version}' -P '{sw_proc}' file.sff " \
              "--config-path {config}".format(
            name=name,
            details=details,
            sw_name=sw_name,
            sw_version=sw_version,
            sw_proc=sw_proc,
            config=self.config_fn,
        )
        for e in extRefs:
            cmd += ' -E {} '.format(' '.join(e))
        args, configs = parse_args(cmd, use_shlex=True)
        gan = modify.GlobalArgsNote(args, configs)
        self.assertEqual(gan.name, name)
        self.assertEqual(gan.details, details)
        self.assertEqual(gan.softwareName, sw_name)
        self.assertEqual(gan.softwareVersion, sw_version)
        self.assertEqual(gan.softwareProcessingDetails, sw_proc)
        for idx, extRef_ in enumerate(gan.externalReferences):
            self.assertCountEqual(
                [extRef_.type, extRef_.otherType, extRef_.value],
                extRefs[idx],
            )
            self.assertIsInstance(extRef_, modify.ExternalReference)
        # add to segmentation
        seg_in = schema.SFFSegmentation()
        seg_out = gan.add_to_segmentation(seg_in)
        self.assertEqual(seg_out.name, name)
        self.assertEqual(seg_out.details, details)
        for idx, extRef_ in enumerate(seg_out.globalExternalReferences):
            self.assertCountEqual(
                [extRef_.type, extRef_.otherType, extRef_.value],
                extRefs[idx]
            )
            self.assertIsInstance(extRef_, schema.SFFExternalReference)
        self.assertEqual(seg_out.software.name, sw_name)
        self.assertEqual(seg_out.software.version, sw_version)
        self.assertEqual(seg_out.software.processingDetails, sw_proc)
        self.assertEqual(seg_out.details, details)
        # edit in segmentation
        name = li.get_sentence()
        sw_name = rw.random_word()
        sw_version = rw.random_word()
        sw_proc = li.get_sentences(sentences=5)
        details = li.get_sentences(sentences=10)
        extRefs = rw.random_words(count=3)
        extRefs1 = rw.random_words(count=3)
        extRefs2 = rw.random_words(count=3)
        cmd_edit = "notes edit -N '{name}' -S '{sw_name}' -V '{sw_version}' -P '{sw_proc}' -D '{details}' -e 2 " \
                   "-E {extRefs} -E {extRefs1} -E {extRefs2} file.sff --config-path {config}".format(
            name=name,
            sw_name=sw_name,
            sw_version=sw_version,
            sw_proc=sw_proc,
            details=details,
            extRefs=' '.join(extRefs),
            extRefs1=' '.join(extRefs1),
            extRefs2=' '.join(extRefs2),
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_edit, use_shlex=True)
        gan_edit = modify.GlobalArgsNote(args, configs)
        seg_out_edit = gan_edit.edit_in_segmentation(seg_out)
        # we have edited the last extref
        self.assertEqual(seg_out_edit.name, name)
        self.assertEqual(seg_out_edit.software.name, sw_name)
        self.assertEqual(seg_out_edit.software.version, sw_version)
        self.assertEqual(seg_out_edit.software.processingDetails, sw_proc)
        self.assertEqual(seg_out_edit.details, details)
        self.assertEqual(
            [seg_out_edit.globalExternalReferences[2].type, seg_out_edit.globalExternalReferences[2].otherType,
             seg_out_edit.globalExternalReferences[2].value],
            extRefs,
        )
        self.assertEqual(
            [seg_out_edit.globalExternalReferences[3].type, seg_out_edit.globalExternalReferences[3].otherType,
             seg_out_edit.globalExternalReferences[3].value],
            extRefs1
        )
        self.assertEqual(
            [seg_out_edit.globalExternalReferences[4].type, seg_out_edit.globalExternalReferences[4].otherType,
             seg_out_edit.globalExternalReferences[4].value],
            extRefs2
        )
        # delete from segmentation
        cmd_del = "notes del -N -S -V -P -D -e 0,1,2,3,4,5 file.sff --config-path {config}".format(
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_del, use_shlex=True)
        gan_del = modify.GlobalArgsNote(args, configs)
        seg_out_del = gan_del.del_from_segmentation(seg_out_edit)
        self.assertIsNone(seg_out_del.name)
        self.assertIsNone(seg_out_del.software.name)
        self.assertIsNone(seg_out_del.software.version)
        self.assertIsNone(seg_out_del.software.processingDetails)
        self.assertIsNone(seg_out_del.details)
        self.assertEqual(seg_out_del.numGlobalExternalReferences, 0)

    def test_ArgsNote(self):
        """Test ArgsNote (construct local notes from command-line arguments)"""
        segment_id = _random_integers(count=1, start=1)
        name = li.get_sentence()
        description = li.get_sentences(sentences=4)
        num = _random_integer(start=1)
        extRefs = [rw.random_words(count=3) for _ in _xrange(3)]
        comps = rw.random_words(count=5)
        macrs = rw.random_words(count=5)
        cmd_add = "notes add -i {segment_id} -s '{name}' -d '{description}' -n {num} -C {comps} -M {macrs} file.sff --config-path {config}".format(
            segment_id=','.join(map(_str, segment_id)),
            name=name,
            description=description,
            num=num,
            comps=','.join(comps),
            macrs=','.join(macrs),
            config=self.config_fn,
        )
        for e in extRefs:
            cmd_add += ' -E {} '.format(' '.join(e))
        args, configs = parse_args(cmd_add, use_shlex=True)
        # add notes
        an_add = modify.ArgsNote(args, configs)
        segment = schema.SFFSegment()
        segment_add = an_add.add_to_segment(segment)
        self.assertEqual(segment_add.biologicalAnnotation.name, name)
        self.assertEqual(segment_add.biologicalAnnotation.description, description)
        self.assertEqual(segment_add.biologicalAnnotation.numberOfInstances, num)
        for idx, extRef_ in enumerate(an_add.externalReferences):
            self.assertCountEqual(
                [extRef_.type, extRef_.otherType, extRef_.value],
                extRefs[idx],
            )
            self.assertIsInstance(extRef_, modify.ExternalReference)
        self.assertCountEqual(segment_add.complexesAndMacromolecules.complexes, comps)
        self.assertIsInstance(segment_add.complexesAndMacromolecules.complexes, schema.SFFComplexes)
        self.assertCountEqual(segment_add.complexesAndMacromolecules.macromolecules, macrs)
        self.assertIsInstance(segment_add.complexesAndMacromolecules.macromolecules, schema.SFFMacromolecules)
        # edit notes
        name = li.get_sentence()
        desc = li.get_sentences(sentences=10)
        num = _random_integer(start=1)
        extRefs = rw.random_words(count=3)
        extRefs1 = rw.random_words(count=3)
        extRefs2 = rw.random_words(count=3)
        comp = rw.random_word()
        macr = rw.random_word()
        cmd_edit = "notes edit -i {segment_id} -s '{name}' -d '{desc}' -n {num} " \
                   "-e 4 -E {extRefs} -E {extRefs1} -E {extRefs2} -c 2 -C {comp} " \
                   "-m 5 -M {macr} file.sff --config-path {config}".format(
            segment_id=','.join(map(_str, segment_id)),
            name=name,
            desc=desc,
            num=num,
            extRefs=' '.join(extRefs),
            extRefs1=' '.join(extRefs1),
            extRefs2=' '.join(extRefs2),
            comp=comp,
            macr=macr,
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_edit, use_shlex=True)
        an_edit = modify.ArgsNote(args, configs)
        segment_edit = an_edit.edit_in_segment(segment_add)
        self.assertEqual(segment_edit.biologicalAnnotation.name, name)
        self.assertEqual(segment_edit.biologicalAnnotation.description, desc)
        self.assertEqual(segment_edit.biologicalAnnotation.numberOfInstances, num)
        self.assertEqual(
            [
                segment_edit.biologicalAnnotation.externalReferences[-3].type,
                segment_edit.biologicalAnnotation.externalReferences[-3].otherType,
                segment_edit.biologicalAnnotation.externalReferences[-3].value
            ],
            extRefs
        )
        self.assertEqual(
            [
                segment_edit.biologicalAnnotation.externalReferences[-2].type,
                segment_edit.biologicalAnnotation.externalReferences[-2].otherType,
                segment_edit.biologicalAnnotation.externalReferences[-2].value
            ],
            extRefs1
        )
        self.assertEqual(
            [
                segment_edit.biologicalAnnotation.externalReferences[-1].type,
                segment_edit.biologicalAnnotation.externalReferences[-1].otherType,
                segment_edit.biologicalAnnotation.externalReferences[-1].value
            ],
            extRefs2
        )
        self.assertEqual(segment_edit.complexesAndMacromolecules.complexes[2], comp)
        self.assertEqual(segment_edit.complexesAndMacromolecules.macromolecules[5], macr)
        # del notes
        cmd_del = "notes del -i {segment_id} -s -d -n -e 0,1,2,3,4,5 -c 0,1,2,3,4 -m 0,1,2,3,4,5 " \
                  "file.sff --config-path {config}".format(
            segment_id=','.join(map(_str, segment_id)),
            config=self.config_fn,
        )
        args, configs = parse_args(cmd_del, use_shlex=True)
        an_del = modify.ArgsNote(args, configs)
        segment_del = an_del.del_from_segment(segment_edit)
        self.assertIsNone(segment_del.biologicalAnnotation.name)
        self.assertIsNone(segment_del.biologicalAnnotation.description)
        self.assertIsNone(segment_del.biologicalAnnotation.numberOfInstances)
        self.assertEqual(segment_del.biologicalAnnotation.numExternalReferences, 0)
        self.assertEqual(segment_del.complexesAndMacromolecules.numComplexes, 0)
        self.assertEqual(segment_del.complexesAndMacromolecules.numMacromolecules, 0)


class TestNotes_find(Py23FixTestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_fn = os.path.join(BASE_DIR, 'sff.conf')

    def test_search_default(self):
        """Test default search parameters"""
        args, configs = parse_args("notes search 'mitochondria' --config-path {}".format(self.config_fn),
                                   use_shlex=True)
        resource = find.SearchResource(args, configs)
        try:
            results = resource.search()
            self.assertGreater(len(results), 0)
        except ValueError as v:
            print(str(v), file=sys.stderr)
            self.assertTrue(False)

    def test_search_no_results(self):
        """Test search that returns no results"""
        # I'm not sure when some biological entity with such a name will be discovered!
        args, configs = parse_args(
            "notes search 'nothing' --exact --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        try:
            results = resource.search()
            self.assertEqual(len(results), 0)
        except ValueError as v:
            print(str(v), file=sys.stderr)
            self.assertTrue(False)

    def test_search_exact_result(self):
        """Test that we get an exact result
            
        NOTE: this test is likely to break as the ontologies get updated
        """
        # this usually returns a single result
        args, configs = parse_args(
            "notes search 'DNA replication licensing factor MCM6' --exact --config-path {}".format(self.config_fn),
            use_shlex=True)
        resource = find.SearchResource(args, configs)
        results = resource.search()
        self.assertEqual(len(results), 2)  # funny!

    def test_search_ontology(self):
        """Test that we can search an ontology"""
        #  this search should bring at least one result
        args, configs = parse_args(
            "notes search 'mitochondria' --exact -O omit --config-path {}".format(self.config_fn), use_shlex=True)
        resource = find.SearchResource(args, configs)
        try:
            results = resource.search()
            self.assertGreaterEqual(len(results), 1)
        except ValueError as v:
            print(str(v), file=sys.stderr)
            self.assertTrue(False)

    def test_search_from_start(self):
        """Test that we can search from the starting index"""
        # this search usually has close to 1000 results; 100 is a reasonable start
        random_start = _random_integer(1, 970)
        args, configs = parse_args("notes search 'mitochondria' --start {} --config-path {}".format(
            random_start,
            self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        try:
            results = resource.search()
            self.assertGreaterEqual(results.structured_response['response']['start'], random_start - 1)
        except ValueError as v:
            print(str(v), file=sys.stderr)
            self.assertTrue(False)

    def test_search_result_rows(self):
        """Test that we get as many result rows as specified"""
        # this search usually has close to 1000 results; 100 is a reasonable start
        random_rows = _random_integer(10, 100)
        args, configs = parse_args("notes search 'mitochondria' --rows {} --config-path {}".format(
            random_rows,
            self.config_fn,
        ), use_shlex=True)
        resource = find.SearchResource(args, configs)
        try:
            results = resource.search()
            self.assertGreaterEqual(len(results), random_rows)
        except ValueError as v:
            print(str(v), file=sys.stderr)
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
