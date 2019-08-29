#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.notes.modify
=======================

Add, edit and delete terms in EMDB-SFF files
"""
from __future__ import division, print_function

import json
import os
import re
import shlex
import sys

import requests
import shutil
from styled import Styled

from . import RESOURCE_LIST_NAMES
from .. import schema
from ..core import _str, _decode, _xrange
from ..core.parser import parse_args
from ..core.print_tools import print_date
from ..notes.view import HeaderView, NoteView
from ..sff import handle_convert

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-07"


# todo: allow user to modify/view hierarchy through segmentation annotation toolkit


class ExternalReference(object):
    """Class definition for a :py:class:`ExternalReference` object"""

    def __init__(self, type_=None, otherType=None, value=None):
        """Initialise an object of class :py:class:`ExternalReference`

        :param type_: the name of the resource
        :param otherType: the IRI at which the resource may be reached
        :param value: the external reference accession code
        """
        self.type = type_
        self.otherType = otherType
        self.value = value
        self.label, self.description = self._get_text()

    @property
    def iri(self):
        """The IRI value should be *double* url-encoded"""
        if sys.version_info[0] > 2:
            from urllib.parse import urlencode
        else:
            from urllib import urlencode
        urlenc = urlencode({u'iri': self.otherType.encode(u'idna')})
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
        if self.type not in RESOURCE_LIST_NAMES:
            url = u"https://www.ebi.ac.uk/ols/api/ontologies/{ontology}/terms/{iri}".format(
                ontology=self.type,
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
                    u"Could not find label and description for external reference {}:{}".format(self.type, self.value))
        elif self.type == u'EMDB':
            url = u"https://www.ebi.ac.uk/pdbe/api/emdb/entry/all/{}".format(self.value)
            R = requests.get(url)
            if R.status_code == 200:
                self._result = json.loads(R.text)
                # label
                label = list(self._result.keys())[0]
                # description
                description = self._result[label][0][u'deposition'][u'title']
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.type, self.value))
        elif self.type == u"PDB":
            url = u"https://www.ebi.ac.uk/pdbe/search/pdb/select?q={}&wt=json".format(self.value)
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
                        u"Could not find label and description for external reference {}:{}".format(self.type,
                                                                                                    self.value))
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.type, self.value))
        elif self.type == u"UniProt":
            url = u"https://www.uniprot.org/uniprot/" \
                  u"?query=accession:{search_term}&format=tab&offset=0&limit=1&columns=id,entry_name," \
                  u"protein_names,organism".format(
                search_term=self.value,
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
                        u"Could not find label and description for external reference {}:{}".format(self.type,
                                                                                                    self.value))
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.type, self.value))
        elif self.type == u'Europe PMC':
            url = u"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=30932919&format=json".format(
                self.value)
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
                            self.type,
                            self.value
                        )
                    )
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.type, self.value))
        elif self.type == u'EMPIAR':
            url = u"https://www.ebi.ac.uk/pdbe/emdb/empiar/api/entry/{}".format(self.value)
            R = requests.get(url)
            if R.status_code == 200:
                self._result = json.loads(R.text)
                try:
                    # label
                    label = self._result[self.value][u"title"]
                    # description
                    description = self._result[self.value][u"experiment_type"]
                except IndexError:
                    print_date(
                        u"Could not find label and description for external reference {}:{}".format(
                            self.type,
                            self.value
                        )
                    )
            else:
                print_date(
                    u"Could not find label and description for external reference {}:{}".format(self.type, self.value))
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
        self._extRefList = list()

    @property
    def externalReferences(self):
        return self._extRefList

    @externalReferences.setter
    def externalReferences(self, value):
        """Assigne directly; must all be ExternalReference objects or lists of strings"""
        self._extRefList = list()  # empty the present list
        for v in value:
            if isinstance(v, ExternalReference):
                self._extRefList.append(v)
            elif isinstance(v, list) or isinstance(v, tuple):
                self._extRefList.append(ExternalReference(*v))


class AbstractGlobalNote(BaseNote):
    """Abstract class definition for global annotations

    Defines attributes of global annotation.

    Also defines three methods that effect the annotation to a segmentation object:

    - :py:func:`add_to_segmentation`

    - :py:func:`edit_in_segmentation`

    - :py:func:`del_from_segmentation`
    """
    name = NoteAttr('name')
    softwareName = NoteAttr('softwareName')
    softwareVersion = NoteAttr('sofwareVersion')
    softwareProcessingDetails = NoteAttr('softwareProcessingDetails')
    details = NoteAttr('details')
    externalReferenceId = NoteAttr('externalReferenceId')

    def add_to_segmentation(self, segmentation):
        """Adds this note to the given segmentation

        :param segmentation: an EMDB-SFF segmentation object
        :type segmentation: :py:class:`sfftk.schema.SFFSegmentation`
        :return segmentation: the EMDB-SFF segmentation with the annotation added
        """
        #  name
        if self.name is not None:
            segmentation.name = self.name
        segmentation.software = schema.SFFSoftware()
        # software name
        if self.softwareName is not None:
            segmentation.software.name = self.softwareName
        # software version
        if self.softwareVersion is not None:
            segmentation.software.version = self.softwareVersion
        #  software processing details
        if self.softwareProcessingDetails is not None:
            segmentation.software.processingDetails = self.softwareProcessingDetails
        # details
        if self.details is not None:
            segmentation.details = self.details
        # global external references
        if self.externalReferences:
            if not segmentation.globalExternalReferences:
                segmentation.globalExternalReferences = schema.SFFGlobalExternalReferences()
            for gExtRef in self.externalReferences:
                segmentation.globalExternalReferences.add_externalReference(
                    schema.SFFExternalReference(
                        type=gExtRef.type,
                        otherType=gExtRef.otherType,
                        value=gExtRef.value,
                        label=gExtRef.label,
                        description=gExtRef.description
                    )
                )
        return segmentation

    def edit_in_segmentation(self, segmentation):
        """Modify the global annotation of the given segmentation
        
        :param segmentation: an EMDB-SFF segmentation object
        :type segmentation: :py:class:`sfftk.schema.SFFSegmentation`
        :return segmentation: the EMDB-SFF segmentation with annotated edited
        :rtype segmentation: :py:class:`sfftk.schema.SFFSegmentation`
        """
        #  name
        if self.name is not None:
            segmentation.name = self.name
        # software name
        if self.softwareName is not None:
            segmentation.software.name = self.softwareName
        # software version
        if self.softwareVersion is not None:
            segmentation.software.version = self.softwareVersion
        #  software processing details
        if self.softwareProcessingDetails is not None:
            segmentation.software.processingDetails = self.softwareProcessingDetails
        # details
        if self.details is not None:
            segmentation.details = self.details
        # external references
        start_index = self.externalReferenceId
        # editing globalExternalReferences starting at index 'start_index'
        # this will result in all subsequent globalExternalReferences being replaced
        # once it gets to the end of the list of gER any additional ones will be appended
        # e.g. if we have 5 gERs and we want to add another 5 but starting at index 4 (the fifth)
        # then we will replace index 4 then keep adding the other new 4 gERs
        # to add new ones use 'notes add -E <extref>'
        for gExtRef in self.externalReferences:
            try:
                segmentation.globalExternalReferences.replace_externalReference(
                    schema.SFFExternalReference(
                        type=gExtRef.type,
                        otherType=gExtRef.otherType,
                        value=gExtRef.value,
                        label=gExtRef.label,
                        description=gExtRef.description
                    ),
                    start_index,
                )
            except IndexError:
                segmentation.globalExternalReferences.add_externalReference(
                    schema.SFFExternalReference(
                        type=gExtRef.type,
                        otherType=gExtRef.otherType,
                        value=gExtRef.value,
                        label=gExtRef.label,
                        description=gExtRef.description
                    )
                )
            start_index += 1
        return segmentation

    def del_from_segmentation(self, segmentation):
        """Delete attributes from a segmentation
        
        :param segmentation: an EMDB-SFF segmentation object
        :type segmentation: :py:class:`sfftk.schema.SFFSegmentation`
        :return segmentation: the EMDB-SFF segmentation with annotation deleted
        :rtype segmentation: :py:class:`sfftk.schema.SFFSegmentation`
        """
        #  name
        if self.name:
            segmentation.name = None
        # software name
        if self.softwareName:
            segmentation.software.name = None
        # software version
        if self.softwareVersion:
            segmentation.software.version = None
        # sofware processing details
        if self.softwareProcessingDetails:
            segmentation.software.processingDetails = None
        # details
        if self.details:
            segmentation.details = None
        # external references
        if self.externalReferenceId:
            if segmentation.globalExternalReferences:
                # current globalExtRefs
                refs = list(segmentation.globalExternalReferences)
                # extract the items to be removed
                to_remove = list()
                for i in self.externalReferenceId:
                    try:
                        to_remove.append(refs[i])
                    except IndexError:
                        print_date(_str(
                            Styled("[[ '{}'|fg-red ]]", "Failed to delete global external reference ID {}".format(i))))
                # now remove them
                for t in to_remove:
                    refs.remove(t)
                segmentation.globalExternalReferences = schema.SFFGlobalExternalReferences(refs)
            else:
                print_date("No global external references to delete from!")
        return segmentation


class GlobalArgsNote(AbstractGlobalNote):
    """Class defining segmentation (global) annotation based on command-line arguments

    :param args: an :py:class:`argparse.Namespace` object
    :param configs: persistent configurations for ``sfftk``
    """

    def __init__(self, args, configs, *args_, **kwargs_):
        super(GlobalArgsNote, self).__init__(*args_, **kwargs_)
        self.name = args.name
        self.configs = configs
        self.softwareName = args.software_name
        self.softwareVersion = args.software_version
        self.softwareProcessingDetails = args.software_processing_details
        self.details = args.details
        if hasattr(args, 'external_ref_id'):
            self.externalReferenceId = args.external_ref_id
        if hasattr(args, 'external_ref'):
            if args.external_ref:
                for _type, _otherType, _value in args.external_ref:
                    self._extRefList.append(
                        ExternalReference(
                            type_=_type,
                            otherType=_otherType,
                            value=_value
                        )
                    )


class AbstractNote(BaseNote):
    """Note 'abstact' class that defines private attributes and main methods"""
    name = NoteAttr('name')
    description = NoteAttr('description')
    numberOfInstances = NoteAttr('numberOfInstances')
    externalReferenceId = NoteAttr('externalReferenceId')
    complexId = NoteAttr('complexId')
    complexes = NoteAttr('complexes')
    macromoleculeId = NoteAttr('macromoleculeId')
    macromolecules = NoteAttr('macromolecules')

    def add_to_segment(self, segment):
        """Add the annotations found in this ``Note`` object to the ``schema.SFFSegment`` object
         
        :param segment: single segment in EMDB-SFF
        :type segment: ``sfftk.schema.SFFSegment``
        """
        # biologicalAnnotation
        bA = segment.biologicalAnnotation
        if self.name is not None:
            bA.name = self.name
        if self.description is not None:
            bA.description = self.description
        # else:
        #     bA.description = segment.biologicalAnnotation.description
        if self.numberOfInstances:
            bA.numberOfInstances = self.numberOfInstances
        # else:
        #     bA.numberOfInstances = segment.biologicalAnnotation.numberOfInstances
        # copy current external references
        bA.externalReferences = segment.biologicalAnnotation.externalReferences
        if self.externalReferences:
            if not bA.externalReferences:
                bA.externalReferences = schema.SFFExternalReferences()
            for extRef in self.externalReferences:
                extRef._get_text()
                bA.externalReferences.add_externalReference(
                    schema.SFFExternalReference(
                        type_=extRef.type,
                        otherType=extRef.otherType,
                        value=extRef.value,
                        label=extRef.label,
                        description=extRef.description
                    )
                )
        segment.biologicalAnnotation = bA
        # complexesAndMacromolecules
        # copy current cAM
        cAM = segment.complexesAndMacromolecules
        #         cAM = schema.SFFComplexesAndMacromolecules()
        if self.complexes:
            complexes = schema.SFFComplexes()
            for c in self.complexes:
                complexes.add_complex(c)
            cAM.complexes = complexes
        else:
            cAM.complexes = segment.complexesAndMacromolecules.complexes
        if self.macromolecules:
            macromolecules = schema.SFFMacromolecules()
            for m in self.macromolecules:
                macromolecules.add_macromolecule(m)
            cAM.macromolecules = macromolecules
        else:
            cAM.macromolecules = segment.complexesAndMacromolecules.macromolecules
        segment.complexesAndMacromolecules = cAM
        return segment

    def edit_in_segment(self, segment):
        """Edit the annotations found in this ``Note`` object to the ``schema.SFFSegment`` object
         
        :param segment: single segment in EMDB-SFF
        :type segment: ``sfftk.schema.SFFSegment``
        """
        # biologicalAnnotation
        if not segment.biologicalAnnotation:
            print_date("Note: no biological annotation was found. You may edit only after adding with 'sff notes add'.")
        else:
            bA = segment.biologicalAnnotation
            # name
            if self.name is not None:
                bA.name = self.name
            # description
            if self.description is not None:
                bA.description = self.description
            # number of instances
            if self.numberOfInstances:
                bA.numberOfInstances = self.numberOfInstances
            # external references
            # editing externalReferences starting at index 'start_index'
            # this will result in all subsequent externalReferences being replaced
            # once it gets to the end of the list of eR any additional ones will be appended
            # e.g. if we have 5 eRs and we want to add another 5 but starting at index 4 (the fifth)
            # then we will replace index 4 then keep adding the other new 4 eRs
            # to add new ones use 'notes add -i <segment_id> -E <extref>'
            start_index = self.externalReferenceId
            for extRef in self.externalReferences:
                if not bA.externalReferences:
                    bA.externalReferences = schema.SFFExternalReferences()
                try:
                    bA.externalReferences.replace_externalReference(
                        schema.SFFExternalReference(
                            type_=extRef.type,
                            otherType=extRef.otherType,
                            value=extRef.value,
                            label=extRef.label,
                            description=extRef.description
                        ),
                        start_index
                    )
                except IndexError:
                    bA.externalReferences.add_externalReference(
                        schema.SFFExternalReference(
                            type_=extRef.type,
                            otherType=extRef.otherType,
                            value=extRef.value,
                            label=extRef.label,
                            description=extRef.description
                        )
                    )
                start_index += 1
            segment.biologicalAnnotation = bA
        # complexesAndMacromolecules
        if not segment.complexesAndMacromolecules:
            print_date(
                "Note: no complexes and macromolecules were found. You may edit only after adding with 'sff notes add'.")
        else:
            cAM = segment.complexesAndMacromolecules
            # complexes
            if self.complexes:
                for i in _xrange(len(self.complexes)):
                    if i == 0:  # there are complexes but editing the first item mentioned
                        try:
                            cAM.complexes.replace_complex_at(self.complexId + i, self.complexes[i])
                        except IndexError:
                            cAM.complexes.add_complex(self.complexes[i])
                    else:  # all other new complexes are inserted after pushing others down
                        try:
                            cAM.complexes.insert_complex_at(self.complexId + i, self.complexes[i])
                        except IndexError:
                            cAM.complexes.add_complex(self.complexes[i])
                # if cAM.complexes:  # complexes already present
                # else:  # no complexes
                #     complexes = schema.SFFComplexes()
                #     for c in self.complexes:
                #         complexes.add_complex(c)
                #     cAM.complexes = complexes
            # macromolecules
            if self.macromolecules:
                for i in _xrange(len(self.macromolecules)):
                    if i == 0:  # there are macromolecules but editing the first item mentioned
                        try:
                            cAM.macromolecules.replace_macromolecule_at(self.macromoleculeId + i,
                                                                        self.macromolecules[i])
                        except IndexError:
                            cAM.macromolecules.add_macromolecule(self.macromolecules[i])
                    else:  # all other new macromolecules are inserted after pushing others down
                        try:
                            cAM.macromolecules.insert_macromolecule_at(self.macromoleculeId + i,
                                                                       self.macromolecules[i])
                        except IndexError:
                            cAM.macromolecules.add_macromolecule(self.macromolecules[i])
                # if cAM.macromolecules:  # macromolecules already present
                # else:  # no macromolecules
                #     macromolecules = schema.SFFMacromolecules()
                #     for m in self.macromolecules:
                #         macromolecules.add_macromolecule(m)
                #     cAM.macromolecules = macromolecules
            segment.complexesAndMacromolecules = cAM
        return segment

    def del_from_segment(self, segment):
        """Delete the annotations found in this ``Note`` object to the ``schema.SFFSegment`` object
         
        :param segment: single segment in EMDB-SFF
        :type segment: ``sfftk.schema.SFFSegment``
        """
        # biologicalAnnotation
        if not segment.biologicalAnnotation:
            print_date("No biological anotation found! Use 'add' to first add a new annotation.")
        else:
            bA = segment.biologicalAnnotation
            if self.name:
                bA.name = None
            if self.description:
                bA.description = None
            if self.numberOfInstances:
                bA.numberOfInstances = None
            if self.externalReferenceId:
                if bA.externalReferences:
                    # current extRefs
                    refs = list(bA.externalReferences)
                    # extract the items to be removed
                    to_remove = list()
                    for i in self.externalReferenceId:
                        try:
                            to_remove.append(refs[i])
                        except IndexError:
                            print_date(
                                _str(Styled("[[ '{}|fg-red ]]", "Failed to delete external reference ID {}".format(i))))
                    # now remove them
                    for t in to_remove:
                        refs.remove(t)
                    bA.externalReferences = schema.SFFExternalReferences(refs)
                else:
                    print_date("No external references to delete from!")
            # if self.externalReferenceId is not None:  # it could be 0, which is valid but False
            #     if bA.externalReferences:
            #         try:
            #             del bA.externalReferences[self.externalReferenceId]  # externalReferences is a list
            #         except IndexError:
            #             print_date("Failed to delete external reference of ID {}".format(self.externalReferenceId))
            #     else:
            #         print_date("No external references to delete from.")
            segment.biologicalAnnotation = bA
        # complexesAndMacromolecules
        if not segment.complexesAndMacromolecules:
            print_date("No complexes and macromolecules found! Use 'add' to first add a new set.")
        else:
            cAM = segment.complexesAndMacromolecules
            # complexes
            if self.complexId is not None:
                comps = list(cAM.complexes)
                # extract the ones to remove
                to_remove = list()
                for i in self.complexId:
                    try:
                        to_remove.append(comps[i])
                    except IndexError:
                        print_date(_str(Styled("[[ '{}'|fg-red ]]", "Failed to delete complex ID {}".format(i))))
                # now remove them
                for t in to_remove:
                    comps.remove(t)
                new_macromolecules = schema.SFFComplexes()
                new_macromolecules.set_complexes(comps)
                cAM.complexes = new_macromolecules
            segment.complexesAndMacromolecules = cAM
            # if self.complexId is not None:
            #     if cAM.complexes:
            #         try:
            #             cAM.complexes.delete_at(self.complexId)
            #         except IndexError:
            #             print_date("Failed to delete macromolecule of ID {}".format(self.complexId))
            #     else:
            #         print_date("No complexes to delete from.")
            # macromolecules
            if self.macromoleculeId is not None:
                macrs = list(cAM.macromolecules)
                # extract the ones to remove
                to_remove = list()
                for i in self.macromoleculeId:
                    try:
                        to_remove.append(macrs[i])
                    except IndexError:
                        print_date(_str(Styled("[[ '{}'|fg-red ]]", "Failed to delete macromolecule ID {}".format(i))))
                # now remove them
                for t in to_remove:
                    macrs.remove(t)
                new_macromolecules = schema.SFFMacromolecules()
                new_macromolecules.set_macromolecules(macrs)
                cAM.macromolecules = new_macromolecules
            segment.complexesAndMacromolecules = cAM
            # if self.macromoleculeId is not None:
            #     if cAM.macromolecules:
            #         try:
            #             cAM.macromolecules.delete_at(self.macromoleculeId)
            #         except IndexError:
            #             print_date("Failed to delete macromolecule of ID {}".format(self.macromoleculeId))
            #     else:
            #         print_date("No macromolecules to delete from.")
            # segment.complexesAndMacromolecules = cAM
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
        self.numberOfInstances = args.number_of_instances
        if hasattr(args, 'external_ref_id'):
            self.externalReferenceId = args.external_ref_id
        # externalReferences
        if hasattr(args, 'external_ref'):  # sff notes del has no -E arg
            if args.external_ref:
                for _type, _otherType, _value in args.external_ref:
                    self._extRefList.append(
                        ExternalReference(
                            type_=_type,
                            otherType=_otherType,
                            value=_value
                        )
                    )
        if hasattr(args, 'complex_id'):
            self.complexId = args.complex_id
        if hasattr(args, 'complexes'):
            self.complexes = args.complexes
        if hasattr(args, 'macromolecule_id'):
            self.macromoleculeId = args.macromolecule_id
        if hasattr(args, 'macromolecules'):
            self.macromolecules = args.macromolecules


class SimpleNote(AbstractNote):
    """Class definition for a :py:class:`SimpleNote` object"""

    def __init__(
            self, name=None, description=None, numberOfInstances=None, externalReferenceId=None,
            externalReferences=None, complexId=None, complexes=None,
            macromoleculeId=None, macromolecules=None, *args, **kwargs
    ):
        """Initialise an :py:class:`SimpleNote` object

        :param str description: the description string of the segment
        :param int numberOfInstances: the number of instances of this segment
        :param int externalReferenceId: ID of an external reference
        :param externalReferences: iterable of external references
        :param complexId: ID of a complex
        :param complexes: iterable of complexes
        :param macromoleculeId: ID of a macromolecule
        :param macromolecules: iterable of macromolecules
        """
        super(SimpleNote, self).__init__(*args, **kwargs)
        self.name = name
        self.description = description
        self.numberOfInstances = numberOfInstances
        self.externalReferenceId = externalReferenceId
        # externalReferences
        if externalReferences:
            for _type, _otherType, _value in externalReferences:
                self._extRefList.append(ExternalReference(type_=_type, otherType=_otherType, value=_value))
        self.complexId = complexId
        self.complexes = complexes
        self.macromoleculeId = macromoleculeId
        self.macromolecules = macromolecules


def add_note(args, configs):
    """Add annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Congif``
    :return int status: status
    """
    sff_seg = schema.SFFSegmentation(args.sff_file)
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
                print(string)
                found_segment = True
        if not found_segment:
            print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    # export
    sff_seg.export(args.sff_file)
    return 0


def edit_note(args, configs):
    """Edit annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Congif``
    :return int status: status
    """
    sff_seg = schema.SFFSegmentation(args.sff_file)
    # global changes
    if args.segment_id is None:
        #  create a GlobalArgsNote object
        global_note = GlobalArgsNote(args, configs)
        # edit the notes in the segmentation
        # editing name, software, filePath, details are exactly the same as adding
        #  editing external references is different:
        # the externalReferenceId refers to the extRef to edit
        # any additionally specified external references (-E a b -E x y) are inserted after the edited index
        sff_seg = global_note.edit_in_segmentation(sff_seg)
        #  show the updated header
        string = Styled(u"[[ ''|fg-green:no-end ]]")
        string += _str(HeaderView(sff_seg))
        string += Styled(u"[[ ''|reset ]]")
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
                print(_str(string))
                found_segment = True
        if not found_segment:
            print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    # export
    sff_seg.export(args.sff_file)
    return 0


def del_note(args, configs):
    """Delete annotation to a segment specified in args
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Congif``
    :return int status: status
    """
    sff_seg = schema.SFFSegmentation(args.sff_file)
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
                print(_str(string))
                found_segment = True
        if not found_segment:
            print_date("Segment of ID(s) {} not found".format(", ".join(map(str, args.segment_id))))
    # export
    sff_seg.export(args.sff_file)
    return 0


def copy_notes(args, configs):
    """Copy notes across segments

    One or more segments can be chosen for either or both source and destination

    :param args: parse arguments
    :param configs: configurations object
    :return: status
    """
    sff_seg = schema.SFFSegmentation(args.sff_file)
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
            print(_str(string))
    # export
    sff_seg.export(args.sff_file)
    return os.EX_OK


def clear_notes(args, configs):
    """Clear notes from segments

    :param args: parse arguments
    :param configs: configurations object
    :return: status
    """
    sff_seg = schema.SFFSegmentation(args.sff_file)
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
        print(_str(string))
    if args.segment_id is not None:
        for segment in sff_seg.segments:
            if segment.id in args.segment_id:
                string = Styled(u"[[ ''|fg-green:no-end ]]")
                string += _str(NoteView(segment, _long=True))
                string += Styled(u"[[ ''|reset ]]")
                print(_str(string))
    elif args.from_all_segments:
        for segment in sff_seg.segments:
            string = Styled(u"[[ ''|fg-green:no-end ]]")
            string += _str(NoteView(segment, _long=True))
            string += Styled(u"[[ ''|reset ]]")
            print(_str(string))

    # export
    sff_seg.export(args.sff_file)
    return os.EX_OK


def merge(args, configs):
    """Merge two EMDB-SFF files
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Congif``
    :return int status: status
    """
    # source
    if args.verbose:
        print_date("Reading in source: {}...".format(args.source))
    source = schema.SFFSegmentation(args.source)
    # destination
    if args.verbose:
        print_date("Reading in destination: {}...".format(args.other))
    other = schema.SFFSegmentation(args.other)
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
    :type args: ``argparse.Namespace``
    :param configs: configurations object
    :type configs: ``sfftk.core.configs.Congif``
    :return int status: status
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
            cmd = shlex.split("convert -v {} -o {}".format(temp_file, args.sff_file))
            _args = parse_args(cmd)
            handle_convert(_args)  #  convert
            print_date("Deleting temp file {}...".format(temp_file))
            os.remove(temp_file)
            assert not os.path.exists(temp_file)
        # temp_file: file.json; args.sff_file: file.sff    merge
        # temp_file: file.json; args.sff_file: file.hff    merge
        elif re.match(r'.*\.json$', temp_file, re.IGNORECASE) and (
                re.match(r'.*\.sff$', args.sff_file, re.IGNORECASE) or re.match(r'.*\.hff$', args.sff_file,
                                                                                re.IGNORECASE)):
            json_seg = schema.SFFSegmentation(temp_file)
            seg = schema.SFFSegmentation(args.sff_file)
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
    :type args: ``argparse.Namespace``
    :param configs: configurations object
	:type configs: ``sfftk.core.configs.Congif``
    :return int status: status
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
