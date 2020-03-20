#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
``sfftk.notes.modify``
=======================

Add, edit and delete terms in EMDB-SFF files
"""
from __future__ import division, print_function

import json
import os
import re
import shutil
import sys

import requests
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core import _str, _decode
from sfftkrw.core.parser import parse_args
from sfftkrw.core.print_tools import print_date
from styled import Styled

from . import RESOURCE_LIST_NAMES
from ..notes.view import HeaderView, NoteView
from ..sff import handle_convert

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-07"


# todo: allow user to modify/view hierarchy through segmentation annotation toolkit


class ExternalReference(object):
    """Class definition for a :py:class:`ExternalReference` object"""

    def __init__(self, resource=None, url=None, accession=None):
        """Initialise an object of class :py:class:`ExternalReference`

        :param type_: the name of the resource
        :param otherType: the IRI at which the resource may be reached
        :param value: the external reference accession code
        """
        self.resource = resource
        self.url = url
        self.accession = accession
        self.label, self.description = self._get_text()

    @property
    def iri(self):
        """The IRI value should be *double* url-encoded"""
        if sys.version_info[0] > 2:
            from urllib.parse import urlencode
        else:
            from urllib import urlencode
        urlenc = urlencode({u'iri': self.url.encode(u'idna')})
        urlenc2 = urlencode({u'iri': urlenc.split(u'=')[1]})
        return _decode(urlenc2.split(u'=')[1], 'utf-8')

    # fixme: perhaps the text should exist already instead of being searched for?
    # this seems to be a special case for OLS
    # the user provides  the name of the resource, the IRI/URL and the accession and this
    # method obtains the text meaning that its implementation would have to depend on
    # the name of the resource i.e. the field from which to extract the text
    # will vary by resource
    def _get_text(self):
        """Get the label and description if they exist"""
        label = None
        description = None
        # only search for label and description if from OLS
        if self.resource not in RESOURCE_LIST_NAMES:
            url = u"https://www.ebi.ac.uk/ols/api/ontologies/{ontology}/terms/{iri}".format(
                ontology=self.resource,
                iri=self.iri,
            )
            R = requests.get(url)
            if R.status_code == 200:
                self._result = json.loads(R.text)
                #  label
                try:
                    label = self._result[u'label']
                except KeyError:
                    label = ''
                #  description
                try:
                    description = self._result[u'description'][0] if self._result[u'description'] else None
                except KeyError:
                    description = ''
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                self.accession))
        elif self.resource == u'EMDB':
            url = u"https://www.ebi.ac.uk/pdbe/api/emdb/entry/all/{}".format(self.accession)
            R = requests.get(url)
            if R.status_code == 200:
                self._result = json.loads(R.text)
                # label
                label = list(self._result.keys())[0]
                # description
                description = self._result[label][0][u'deposition'][u'title']
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                self.accession))
        elif self.resource == u"PDB":
            url = u"https://www.ebi.ac.uk/pdbe/search/pdb/select?q={}&wt=json".format(self.accession)
            R = requests.get(url)
            if R.status_code == 200:
                self._result = json.loads(R.text)
                try:
                    # label
                    label = self._result[u'response'][u'docs'][0][u'title']
                    # description
                    description = u"; ".join(self._result[u'response'][u'docs'][0][u'organism_scientific_name'])
                except IndexError:
                    print_date(
                        u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                    self.accession))
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                self.accession))
        elif self.resource == u"UniProt":
            url = u"https://www.uniprot.org/uniprot/" \
                  u"?query=accession:{search_term}&format=tab&offset=0&limit=1&columns=id,entry_name," \
                  u"protein_names,organism".format(
                search_term=self.accession,
            )
            R = requests.get(url)
            if R.status_code == 200:
                self._result = R.text
                try:
                    # split rows; split columns; dump first and last rows
                    _structured_results = list(map(lambda r: r.split('\t'), self._result.split('\n')))[1:-1]
                    # make a list of dicts with the given ids
                    structured_results = list(map(lambda r: dict(zip([u'id', u'name', u'proteins', u'organism'], r)),
                                                  _structured_results))[0]
                    # label
                    label = structured_results[u'name']
                    # description
                    description = u"{} (Organism: {})".format(structured_results[u'proteins'],
                                                              structured_results[u'organism'])
                except ValueError as v:
                    print_date(u"Unknown exception: {}".format(str(v)))
                except IndexError:
                    print_date(
                        u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                    self.accession))
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                self.accession))
        elif self.resource == u'Europe PMC':
            url = u"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=30932919&format=json".format(
                self.accession)
            R = requests.get(url)
            if R.status_code == 200:
                self._result = json.loads(R.text)
                try:
                    # label
                    label = self._result[u"resultList"][u"result"][0][u"authorString"]
                    # description
                    description = self._result[u"resultList"][u"result"][0][u"title"]
                except IndexError:
                    print_date(
                        u"Could not find label and description for external reference {}:{}".format(
                            self.resource,
                            self.accession
                        )
                    )
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                self.accession))
        elif self.resource == u'EMPIAR':
            url = u"https://www.ebi.ac.uk/pdbe/emdb/empiar/api/entry/{}".format(self.accession)
            R = requests.get(url)
            if R.status_code == 200:
                self._result = json.loads(R.text)
                try:
                    # label
                    label = self._result[self.accession][u"title"]
                    # description
                    description = self._result[self.accession][u"experiment_type"]
                except IndexError:
                    print_date(
                        u"Could not find label and description for external reference {}:{}".format(
                            self.resource,
                            self.accession
                        )
                    )
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.resource,
                                                                                                self.accession))
        return label, description


class NoteAttr(object):
    """Descriptor class for note attributes

    :param initval: the initial value of the attribute (default: :py:class:`None`)
    :param str name: the name of the variable (default: 'var')
    """

    def __init__(self, initval=None, name='var'):
        self.val = initval
        self.name = name

    def __get__(self, obj, _):
        return self.val

    def __set__(self, obj, val):
        self.val = val


# todo: attribute type checking


class BaseNote(object):
    """Note base class"""

    def __init__(self):
        self._ext_ref_list = list()

    @property
    def external_references(self):
        return self._ext_ref_list

    @external_references.setter
    def external_references(self, value):
        """Assigne directly; must all be ExternalReference objects or lists of strings"""
        self._ext_ref_list = list()  # empty the present list
        for v in value:
            if isinstance(v, ExternalReference):
                self._ext_ref_list.append(v)
            elif isinstance(v, list) or isinstance(v, tuple):
                self._ext_ref_list.append(ExternalReference(*v))


class AbstractGlobalNote(BaseNote):
    """Abstract class definition for global annotations

    Defines attributes of global annotation.

    Also defines three methods that effect the annotation to a segmentation object:

    - :py:func:`add_to_segmentation`

    - :py:func:`edit_in_segmentation`

    - :py:func:`del_from_segmentation`
    """
    name = NoteAttr('name')
    software_name = NoteAttr('software_name')
    software_version = NoteAttr('sofwareVersion')
    software_processing_details = NoteAttr('software_processing_details')
    details = NoteAttr('details')
    external_reference_id = NoteAttr('external_reference_id')

    def add_to_segmentation(self, segmentation):
        """Adds this note to the given segmentation

        :param segmentation: an EMDB-SFF segmentation object
        :type segmentation: :py:class:`sfftkrw.SFFSegmentation`
        :return segmentation: the EMDB-SFF segmentation with the annotation added
        """
        #  name
        if self.name is not None:
            segmentation.name = self.name
        # to ensure we don't have any id collisions
        if segmentation.software_list:
            max_id = max(list(segmentation.software_list.get_ids()))
            software = schema.SFFSoftware(id=max_id + 1)
        else:
            segmentation.software_list = schema.SFFSoftwareList()
            software = schema.SFFSoftware()
        # software name
        if self.software_name is not None:
            software.name = self.software_name
        # software version
        if self.software_version is not None:
            software.version = self.software_version
        #  software processing details
        if self.software_processing_details is not None:
            software.processing_details = self.software_processing_details
        segmentation.software_list.append(software)
        # details
        if self.details is not None:
            segmentation.details = self.details
        # global external references
        if self.external_references:
            if not segmentation.global_external_references:
                segmentation.global_external_references = schema.SFFGlobalExternalReferenceList()
            for g_ext_ref in self.external_references:
                segmentation.global_external_references.append(
                    schema.SFFExternalReference(
                        resource=g_ext_ref.resource,
                        url=g_ext_ref.url,
                        accession=g_ext_ref.accession,
                        label=g_ext_ref.label,
                        description=g_ext_ref.description
                    )
                )
        return segmentation

    def edit_in_segmentation(self, segmentation):
        """Modify the global annotation of the given segmentation
        
        :param segmentation: an EMDB-SFF segmentation object
        :type segmentation: :py:class:`sfftkrw.SFFSegmentation`
        :return segmentation: the EMDB-SFF segmentation with annotated edited
        :rtype segmentation: :py:class:`sfftkrw.SFFSegmentation`
        """
        #  name
        if self.name is not None:
            segmentation.name = self.name
        # get the software to be edited
        try:
            software = segmentation.software_list.get_by_id(self.software_id)
        except KeyError:
            software = None
        if software is not None:
            # software name
            if self.software_name is not None:
                software.name = self.software_name
            # software version
            if self.software_version is not None:
                software.version = self.software_version
            #  software processing details
            if self.software_processing_details is not None:
                software.processing_details = self.software_processing_details
        # details
        if self.details is not None:
            segmentation.details = self.details
        # external references
        start_index = self.external_reference_id
        # editing global_external_references starting at index 'start_index'
        # this will result in all subsequent global_external_references being replaced
        # once it gets to the end of the list of gER any additional ones will be appended
        # e.g. if we have 5 gERs and we want to add another 5 but starting at index 4 (the fifth)
        # then we will replace index 4 then keep adding the other new 4 gERs
        # to add new ones use 'notes add -E <extref>'
        for g_ext_ref in self.external_references:
            ext_ref = schema.SFFExternalReference(
                resource=g_ext_ref.resource,
                url=g_ext_ref.url,
                accession=g_ext_ref.accession,
                label=g_ext_ref.label,
                description=g_ext_ref.description
            )
            try:
                segmentation.global_external_references.insert(
                    start_index,
                    ext_ref,
                )
            except IndexError:
                segmentation.global_external_references.append(
                    ext_ref
                )
            start_index += 1
        return segmentation

    def del_from_segmentation(self, segmentation):
        """Delete attributes from a segmentation
        
        :param segmentation: an EMDB-SFF segmentation object
        :type segmentation: :py:class:`sfftkrw.SFFSegmentation`
        :return segmentation: the EMDB-SFF segmentation with annotation deleted
        :rtype segmentation: :py:class:`sfftkrw.SFFSegmentation`
        """
        #  name
        if self.name:
            segmentation.name = None
        # software
        for software_id in self.software_id:
            try:
                software = segmentation.software_list.get_by_id(software_id)
            except KeyError:
                software = None
            if software is not None:
                segmentation.software_list.remove(software)
        # details
        if self.details:
            segmentation.details = None
        # external references
        if self.external_reference_id:
            if segmentation.global_external_references:
                # current globalExtRefs
                # fixme: should not cast!!!
                # extract the items to be removed
                to_remove = list()
                for i in self.external_reference_id:
                    try:
                        to_remove.append(segmentation.global_external_references[i])
                    except IndexError:
                        print_date(_str(
                            Styled("[[ '{}'|fg-red ]]", "Failed to delete global external reference ID {}".format(i))))
                # now remove them
                for t in to_remove:
                    segmentation.global_external_references.remove(t)
                # segmentation.global_external_references = schema.SFFGlobalExternalReferenceList(refs)
            else:
                print_date("No global external references to delete from!")
        return segmentation

    def __repr__(self):
        return u"{class_name}(name={name}, software_name={software_name}, software_version={software_version}, " \
               u"software_processing_details={software_processing_details}, details={details}, external_ref_id={external_ref_id})".format(
            class_name=self.__class__,
            name=self.name,
            software_name=self.software_name,
            software_version=self.software_version,
            software_processing_details=self.software_processing_details,
            details=self.details,
            external_ref_id=self.external_reference_id,
        )


class GlobalArgsNote(AbstractGlobalNote):
    """Class defining segmentation (global) annotation based on command-line arguments

    :param args: an :py:class:`argparse.Namespace` object
    :param configs: persistent configurations for ``sfftk``
    """

    def __init__(self, args, configs, *args_, **kwargs_):
        super(GlobalArgsNote, self).__init__(*args_, **kwargs_)
        self.name = args.name if hasattr(args, 'name') else None
        self.configs = configs
        self.software_id = args.software_id if hasattr(args, 'software_id') else None
        self.software_name = args.software_name
        self.software_version = args.software_version
        self.software_processing_details = args.software_processing_details
        self.details = args.details
        if hasattr(args, 'external_ref_id'):
            self.external_reference_id = args.external_ref_id
        if hasattr(args, 'external_ref'):
            if args.external_ref:
                for resource, url, accession in args.external_ref:
                    self._ext_ref_list.append(
                        ExternalReference(
                            resource=resource,
                            url=url,
                            accession=accession
                        )
                    )


class AbstractNote(BaseNote):
    """Note 'abstact' class that defines private attributes and main methods"""
    name = NoteAttr('name')
    description = NoteAttr('description')
    number_of_instances = NoteAttr('number_of_instances')
    external_reference_id = NoteAttr('external_reference_id')

    def add_to_segment(self, segment):
        """Add the annotations found in this ``Note`` object to the :py:class:`sfftkrw.SFFSegment` object
         
        :param segment: single segment in EMDB-SFF
        :type segment: :py:class:`sfftkrw.SFFSegment`
        """
        # biological_annotation
        if not segment.biological_annotation:
            segment.biological_annotation = schema.SFFBiologicalAnnotation()
        bA = segment.biological_annotation
        if self.name is not None:
            bA.name = self.name
        if self.description is not None:
            bA.description = self.description
        # else:
        #     bA.description = segment.biological_annotation.description
        if self.number_of_instances:
            bA.number_of_instances = self.number_of_instances
        # else:
        #     bA.number_of_instances = segment.biological_annotation.number_of_instances
        # copy current external references
        bA.external_references = segment.biological_annotation.external_references
        if self.external_references:
            if not bA.external_references:
                bA.external_references = schema.SFFExternalReferenceList()
            for ext_ref in self.external_references:
                ext_ref._get_text()
                bA.external_references.append(
                    schema.SFFExternalReference(
                        resource=ext_ref.resource,
                        url=ext_ref.url,
                        accession=ext_ref.accession,
                        label=ext_ref.label,
                        description=ext_ref.description
                    )
                )
        segment.biological_annotation = bA
        return segment

    def edit_in_segment(self, segment):
        """Edit the annotations found in this ``Note`` object to the :py:class:`sfftkrw.SFFSegment` object
         
        :param segment: single segment in EMDB-SFF
        :type segment: :py:class:`sfftkrw.SFFSegment`
        """
        # biological_annotation
        if not segment.biological_annotation:
            print_date("Note: no biological annotation was found. You may edit only after adding with 'sff notes add'.")
        else:
            bA = segment.biological_annotation
            # name
            if self.name is not None:
                bA.name = self.name
            # description
            if self.description is not None:
                bA.description = self.description
            # number of instances
            if self.number_of_instances:
                bA.number_of_instances = self.number_of_instances
            # external references
            # editing external_references starting at index 'start_index'
            # this will result in all subsequent external_references being replaced
            # once it gets to the end of the list of eR any additional ones will be appended
            # e.g. if we have 5 eRs and we want to add another 5 but starting at index 4 (the fifth)
            # then we will replace index 4 then keep adding the other new 4 eRs
            # to add new ones use 'notes add -i <segment_id> -E <extref>'
            start_index = self.external_reference_id
            for ext_ref in self.external_references:
                if not bA.external_references:
                    bA.external_references = schema.SFFExternalReferenceList()
                reference = schema.SFFExternalReference(
                    resource=ext_ref.resource,
                    url=ext_ref.url,
                    accession=ext_ref.accession,
                    label=ext_ref.label,
                    description=ext_ref.description
                )
                try:
                    bA.external_references.insert(
                        start_index,
                        reference,
                    )
                except IndexError:
                    bA.external_references.append(
                        reference
                    )
                start_index += 1
            segment.biological_annotation = bA
        return segment

    def del_from_segment(self, segment):
        """Delete the annotations found in this ``Note`` object to the :py:class:`sfftkrw.SFFSegment` object
         
        :param segment: single segment in EMDB-SFF
        :type segment: :py:class:`sfftkrw.SFFSegment`
        """
        # biological_annotation
        if not segment.biological_annotation:
            print_date("No biological anotation found! Use 'add' to first add a new annotation.")
        else:
            bA = segment.biological_annotation
            if self.name:
                bA.name = None
            if self.description:
                bA.description = None
            if self.number_of_instances:
                bA.number_of_instances = None
            if self.external_reference_id:
                if bA.external_references:
                    # current extRefs
                    refs = list(bA.external_references)
                    # extract the items to be removed
                    to_remove = list()
                    for i in self.external_reference_id:
                        try:
                            to_remove.append(refs[i])
                        except IndexError:
                            print_date(
                                _str(Styled("[[ '{}|fg-red ]]", "Failed to delete external reference ID {}".format(i))))
                    # now remove them
                    for t in to_remove:
                        refs.remove(t)
                    bA.external_references = schema.SFFExternalReferenceList(refs)
                else:
                    print_date("No external references to delete from!")
            # if self.external_reference_id is not None:  # it could be 0, which is valid but False
            #     if bA.external_references:
            #         try:
            #             del bA.external_references[self.external_reference_id]  # external_references is a list
            #         except IndexError:
            #             print_date("Failed to delete external reference of ID {}".format(self.external_reference_id))
            #     else:
            #         print_date("No external references to delete from.")
            segment.biological_annotation = bA
        return segment


class ArgsNote(AbstractNote):
    """Class definition for an ArgsNote object"""

    def __init__(self, args, configs, *args_, **kwargs_):
        """Initialise an :py:class:`ArgsNote` object

        :param args: an :py:class:`argparse.Namespace` object
        :params configs: ``sfftk`` persistent configs (see :py:mod:`sfftk.config` documentation)
        """
        super(ArgsNote, self).__init__(*args_, **kwargs_)
        self.name = args.segment_name
        self.description = args.description
        self.number_of_instances = args.number_of_instances
        if hasattr(args, 'external_ref_id'):
            self.external_reference_id = args.external_ref_id
        # external_references
        if hasattr(args, 'external_ref'):  # sff notes del has no -E arg
            if args.external_ref:
                for resource, url, accession in args.external_ref:
                    self._ext_ref_list.append(
                        ExternalReference(
                            resource=resource,
                            url=url,
                            accession=accession
                        )
                    )


class SimpleNote(AbstractNote):
    """Class definition for a :py:class:`SimpleNote` object"""

    def __init__(
            self, name=None, description=None, number_of_instances=None, external_reference_id=None,
            external_references=None, *args, **kwargs
    ):
        """Initialise an :py:class:`SimpleNote` object

        :param str description: the description string of the segment
        :param int number_of_instances: the number of instances of this segment
        :param int external_reference_id: ID of an external reference
        :param external_references: iterable of external references
        """
        super(SimpleNote, self).__init__(*args, **kwargs)
        self.name = name
        self.description = description
        self.number_of_instances = number_of_instances
        self.external_reference_id = external_reference_id
        # external_references
        if external_references:
            for resource, url, accession in external_references:
                self._ext_ref_list.append(
                    ExternalReference(
                        resource=resource,
                        url=url,
                        accession=accession
                    )
                )


def add_note(args, configs):
    """Add annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    sff_seg = schema.SFFSegmentation.from_file(args.sff_file)
    # global changes
    if args.segment_id is None:
        # create a GlobalArgsNote object
        global_note = GlobalArgsNote(args, configs)
        # add notes to segmentation
        sff_seg = global_note.add_to_segmentation(sff_seg)
        # show the updated header
        string = Styled(u"[[ ''|fg-green:no-end ]]")
        string += _str(HeaderView(sff_seg))
        string += Styled(u"[[ ''|reset ]]")
        # fixme: use print_date
        print(_str(string))
    else:
        found_segment = False
        for segment in sff_seg.segments:
            if segment.id in args.segment_id:
                note = ArgsNote(args, configs)
                sff_seg.segment = note.add_to_segment(segment)
                string = Styled(u"[[ ''|fg-green:no-end ]]")
                string += _str(NoteView(sff_seg.segment, _long=True))
                string += Styled(u"[[ ''|reset ]]")
                # fixme: use print_date
                print(string)
                found_segment = True
        if not found_segment:
            print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    # export
    sff_seg.export(args.sff_file)
    return os.EX_OK


def edit_note(args, configs):
    """Edit annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    sff_seg = schema.SFFSegmentation.from_file(args.sff_file)
    # global changes
    if args.segment_id is None:
        #  create a GlobalArgsNote object
        global_note = GlobalArgsNote(args, configs)
        # edit the notes in the segmentation
        # editing name, software, filePath, details are exactly the same as adding
        #  editing external references is different:
        # the external_reference_id refers to the extRef to edit
        # any additionally specified external references (-E a b -E x y) are inserted after the edited index
        sff_seg = global_note.edit_in_segmentation(sff_seg)
        #  show the updated header
        string = Styled(u"[[ ''|fg-green:no-end ]]")
        string += _str(HeaderView(sff_seg))
        string += Styled(u"[[ ''|reset ]]")
        # fixme: use print_date
        print(_str(string))
    else:
        found_segment = False
        for segment in sff_seg.segments:
            if segment.id in args.segment_id:
                note = ArgsNote(args, configs)
                sff_seg.segment = note.edit_in_segment(segment)
                string = Styled(u"[[ ''|fg-green:no-end ]]")
                string += _str(NoteView(sff_seg.segment, _long=True))
                string += Styled(u"[[ ''|reset ]]")
                # fixme: use print_date
                print(_str(string))
                found_segment = True
        if not found_segment:
            print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    # export
    sff_seg.export(args.sff_file)
    return os.EX_OK


def del_note(args, configs):
    """Delete annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    sff_seg = schema.SFFSegmentation.from_file(args.sff_file)
    # global changes
    if args.segment_id is None:
        # create a GlobalArgsNote object
        global_note = GlobalArgsNote(args, configs)
        # delete the notes from segmentation
        sff_seg = global_note.del_from_segmentation(sff_seg)
        #  show the updated header
        string = Styled(u"[[ ''|fg-green:no-end ]]")
        string += _str(HeaderView(sff_seg))
        string += Styled(u"[[ ''|reset ]]")
        # fixme: use print_date
        print(_str(string))
    else:
        found_segment = False
        for segment in sff_seg.segments:
            if segment.id in args.segment_id:
                note = ArgsNote(args, configs)
                sff_seg.segment = note.del_from_segment(segment)
                string = Styled(u"[[ ''|fg-green:no-end ]]")
                string += _str(NoteView(sff_seg.segment, _long=True))
                string += Styled(u"[[ ''|reset ]]")
                # fixme: use print_date
                print(_str(string))
                found_segment = True
        if not found_segment:
            print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    # export
    sff_seg.export(args.sff_file)
    return os.EX_OK


def copy_notes(args, configs):
    """Copy notes across segments

    One or more segments can be chosen for either or both source and destination

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    sff_seg = schema.SFFSegmentation.from_file(args.sff_file)
    # from segment
    from_segment = list()
    if args.segment_id is not None:
        from_segment = args.segment_id
    if args.from_global:
        try:
            from_segment.append(-1)
        except NameError:
            from_segment = [-1]
    # to_segment
    to_segment = list()
    if args.to_segment is not None:
        to_segment = args.to_segment
    elif args.to_all:
        all_segment_ids = set(sff_seg.segments.get_ids())
        to_segment = list(all_segment_ids.difference(set(from_segment)))
    if args.to_global:
        try:
            to_segment.append(-1)
        except NameError:
            to_segment = [-1]
    for f in from_segment:
        for t in to_segment:
            sff_seg.copy_annotation(f, t)
            string = Styled(u"[[ ''|fg-green:no-end ]]")
            if t == -1:
                string += _str(HeaderView(sff_seg))
            else:
                string += _str(NoteView(sff_seg.segments.get_by_id(t), _long=True))
            string += Styled(u"[[ ''|reset ]]")
            # fixme: use print_date
            print(_str(string))
    # export
    sff_seg.export(args.sff_file)
    return os.EX_OK


def clear_notes(args, configs):
    """Clear notes from segments

    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    sff_seg = schema.SFFSegmentation.from_file(args.sff_file)
    from_segment = list()
    if args.segment_id is not None:
        from_segment = args.segment_id
    elif args.from_all_segments:
        from_segment = list(sff_seg.segments.get_ids())
    if args.from_global:
        try:
            from_segment.append(-1)
        except NameError:
            from_segment = [-1]
    # fixme: sff notes clear emd_5625.sff raises UnboundLocalError: local variable
    #  'from_segment' referenced before assignment
    for f in from_segment:
        sff_seg.clear_annotation(f)
    if args.from_global:
        string = Styled(u"[[ ''|fg-green:no-end ]]")
        string += _str(HeaderView(sff_seg))
        string += Styled(u"[[ ''|reset ]]")
        # fixme: use print_date
        print(_str(string))
    if args.segment_id is not None:
        for segment in sff_seg.segments:
            if segment.id in args.segment_id:
                string = Styled(u"[[ ''|fg-green:no-end ]]")
                string += _str(NoteView(segment, _long=True))
                string += Styled(u"[[ ''|reset ]]")
                # fixme: use print_date
                print(_str(string))
    elif args.from_all_segments:
        for segment in sff_seg.segments:
            string = Styled(u"[[ ''|fg-green:no-end ]]")
            string += _str(NoteView(segment, _long=True))
            string += Styled(u"[[ ''|reset ]]")
            # fixme: use print_date
            print(_str(string))

    # export
    sff_seg.export(args.sff_file)
    return os.EX_OK


def merge(args, configs):
    """Merge notes from two EMDB-SFF files
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    # source
    if args.verbose:
        print_date("Reading in source: {}...".format(args.source))
    source = schema.SFFSegmentation.from_file(args.source)
    # destination
    if args.verbose:
        print_date("Reading in destination: {}...".format(args.other))
    other = schema.SFFSegmentation.from_file(args.other)
    if args.verbose:
        print_date("Merging annotations...")
    other.merge_annotation(source)
    # export
    if args.verbose:
        print_date("Writing output to {}".format(args.output))
    other.export(args.output)
    if args.verbose:
        print_date("Done")
    return os.EX_OK


def save(args, configs):
    """Save changes made
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    temp_file = configs['__TEMP_FILE']
    if os.path.exists(temp_file):
        # temp_file: file.sff; args.sff_file: file.sff     copy
        # temp_file: file.hff; args.sff_file: file.hff     copy
        # temp_file: file.json; args.sff_file: file.json   copy
        if (re.match(r'.*\.sff$', temp_file, re.IGNORECASE) and re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE)) or \
                (re.match(r'.*\.hff$', temp_file, re.IGNORECASE) and re.match(r'.*\.hff$', args.sff_file,
                                                                              re.IGNORECASE)) or \
                (re.match(r'.*\.json$', temp_file, re.IGNORECASE) and re.match(r'.*\.json$', args.sff_file,
                                                                               re.IGNORECASE)):
            print_date("Copying temp file {} to {}...".format(temp_file, args.sff_file))
            shutil.copy(temp_file, args.sff_file)
            print_date("Deleting temp file {}...".format(temp_file))
            os.remove(temp_file)
            assert not os.path.exists(temp_file)
        # temp_file: file.sff; args.sff_file: file.hff     convert
        # temp_file: file.sff; args.sff_file: file.json    convert
        # temp_file: file.hff; args.sff_file: file.sff     convert
        # temp_file: file.hff; args.sff_file: file.json    convert
        elif (re.match(r'.*\.sff$', temp_file, re.IGNORECASE) and (
                re.match(r'.*\.hff$', args.sff_file, re.IGNORECASE) or re.match(r'.*\.json$', args.sff_file,
                                                                                re.IGNORECASE))) or \
                (re.match(r'.*\.hff$', temp_file, re.IGNORECASE) and (
                        re.match(r'.*\.json$', args.sff_file, re.IGNORECASE) or re.match(r'.*\.sff$', args.sff_file,
                                                                                         re.IGNORECASE))):
            cmd = "convert -v {} -o {}".format(temp_file, args.sff_file)
            _args = parse_args(cmd, use_shlex=True)
            handle_convert(_args)  #  convert
            print_date("Deleting temp file {}...".format(temp_file))
            os.remove(temp_file)
            assert not os.path.exists(temp_file)
        # temp_file: file.json; args.sff_file: file.sff    merge
        # temp_file: file.json; args.sff_file: file.hff    merge
        elif re.match(r'.*\.json$', temp_file, re.IGNORECASE) and (
                re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE) or re.match(r'.*\.hff$', args.sff_file,
                                                                                re.IGNORECASE)):
            json_seg = schema.SFFSegmentation.from_file(temp_file)
            seg = schema.SFFSegmentation.from_file(args.sff_file)
            #  merge
            seg.merge_annotation(json_seg)
            seg.export(args.sff_file)
            print_date("Deleting temp file {}...".format(temp_file))
            os.remove(temp_file)
            assert not os.path.exists(temp_file)
        else:
            print_date("Unknown file type: {}".format(args.sff_file))
            return os.EX_USAGE
        return os.EX_OK
    else:
        print_date(
            "Missing temp file {}. First perform some edit actions ('add', 'edit', 'del') before trying to save.".format(
                temp_file))
        return os.EX_USAGE


def trash(args, configs):
    """Trash changes made
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :param configs: configurations object
    :type configs: :py:class:`sfftk.core.configs.Configs`
    :return status: status
    :rtype status: int
    """
    temp_file = configs['__TEMP_FILE']
    if os.path.exists(temp_file):
        print_date("Discarding all changes made in temp file {}...".format(temp_file), newline=False)
        os.remove(temp_file)
        assert not os.path.exists(temp_file)
        print_date("Done", incl_date=False)
        return os.EX_OK
    else:
        print_date("Unable to discard with missing temp file {}. No changes made.".format(temp_file))
        return os.EX_DATAERR
