#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.notes.view
=============================

Display notes in EMDB-SFF files
"""
from __future__ import division, print_function

import os
import sys
import textwrap

from styled import Styled

from .. import schema
from ..core import _str
from ..core.print_tools import print_date

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-04-07"
__updated__ = '2018-02-14'


def _add_index(L, pre="\t"):
    """Add indexes to items in L"""
    LL = list()
    i = 0
    for l in L:
        LL.append("{}{}: {}".format(pre, i, l))
        i += 1
    return LL


class View(object):
    """View base class"""
    DISPLAY_WIDTH = 110
    NOT_DEFINED = u"-*- NOT DEFINED -*-"
    NOT_DEFINED_ALT = u"N/A"
    LINE1 = (u'=' * DISPLAY_WIDTH)
    LINE2 = (u'-' * DISPLAY_WIDTH)
    LINE3 = (u'*' * DISPLAY_WIDTH)


class NoteView(View):
    """NoteView class
    
    Display annotation for a single segment
    """

    def __init__(self, segment, _long=False, list_ids=False):
        self._segment = segment
        self._long = _long
        self.list_ids = list_ids

    @property
    def id(self):
        return self._segment.id

    @property
    def parentID(self):
        return self._segment.parentID

    @property
    def name(self):
        if self._segment.biologicalAnnotation.name:
            return self._segment.biologicalAnnotation.name
        else:
            return self.NOT_DEFINED

    @property
    def description(self):
        if self._segment.biologicalAnnotation.description:
            return textwrap.fill(self._segment.biologicalAnnotation.description, self.DISPLAY_WIDTH)
        else:
            return self.NOT_DEFINED

    @property
    def numberOfInstances(self):
        if self._segment.biologicalAnnotation.numberOfInstances:
            return self._segment.biologicalAnnotation.numberOfInstances
        else:
            return self.NOT_DEFINED_ALT

    @property
    def numberOfExternalReferences(self):
        return self._segment.biologicalAnnotation.numExternalReferences

    @property
    def externalReferences(self):
        if self._segment.biologicalAnnotation:
            string_list = list()
            string_list.append(
                u"\t{:>3} {:<16} {:<56} {:<20} {:1} {:1}".format(
                    u"#",
                    u"resource",
                    u"iri",
                    u"short_form",
                    u"L",
                    u"D",
                )
            )
            string_list.append(u"\t" + u"-" * (self.DISPLAY_WIDTH - len(u"\t".expandtabs())))
            i = 0
            for extRef in self._segment.biologicalAnnotation.externalReferences:
                type_ = extRef.type
                otherType = extRef.otherType
                value = extRef.value
                label = u"Y" if extRef.label is not None else u"N"
                description = u"Y" if extRef.description is not None else u"N"
                string_list.append(
                    u"\t{id:>2}: {type:<16} {otherType:<56} {value:<20} {label:1} {description:1}".format(
                        id=i,
                        type=type_,
                        otherType=otherType,
                        value=value,
                        label=label,
                        description=description,
                    )
                )
                i += 1
            return "\n".join(string_list)
        else:
            return "\t" + self.NOT_DEFINED

    @property
    def numberOfComplexes(self):
        return self._segment.complexesAndMacromolecules.numComplexes

    @property
    def complexes(self):
        if self._segment.complexesAndMacromolecules:
            return "\n".join(_add_index(self._segment.complexesAndMacromolecules.complexes))
        else:
            return "\t" + self.NOT_DEFINED

    @property
    def numberOfMacromolecules(self):
        return self._segment.complexesAndMacromolecules.numMacromolecules

    @property
    def macromolecules(self):
        if self._segment.complexesAndMacromolecules:
            return "\n".join(_add_index(self._segment.complexesAndMacromolecules.macromolecules))
        else:
            return "\t" + self.NOT_DEFINED

    @property
    def colour(self):
        if self._segment.colour.value:
            return self._segment.colour.value
        else:
            return self.NOT_DEFINED

    @property
    def segmentType(self):
        segment_type = list()
        if self._segment.meshes:
            segment_type.append(u"meshList")
        if self._segment.shapes:
            segment_type.append(u"shapePrimitiveList")
        if self._segment.volume:
            segment_type.append(u"threeDVolume")
        # json EMDB-SFF files do not have geometrical data
        if not segment_type:
            return None
        else:
            return u", ".join(segment_type)

    if sys.version_info[0] > 2:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            if self._long:
                string = u"""\
                \r{}
                \rID:\t\t{}
                \rPARENT ID:\t{}
                \rSegment Type:\t{}
                \r{}
                \rName:
                \r\t{}
                \rDescription:
                \r\t{}
                \rNumber of instances:
                \r\t{}
                \r{}
                \rExternal references:
                \r{}
                \r{}
                \rComplexes:
                \r{}
                \rMacromolecules:
                \r{}
                \r{}
                \rColour:
                \r\t{}\
                """.format(
                    # ****
                    self.LINE3,
                    self.id,
                    self.parentID,
                    self.segmentType,
                    # ---
                    self.LINE2,
                    self.name,
                    self.description,
                    self.numberOfInstances,
                    # -----
                    self.LINE2,
                    self.externalReferences,
                    # ----
                    self.LINE2,
                    self.complexes,
                    self.macromolecules,
                    # ----
                    self.LINE2,
                    self.colour,
                )
            elif self.list_ids:
                string = u"{}".format(self.id)
            else:
                colour = self.colour
                string = u"{:<7} {:<7} {:<40} {:>5} {:>5} {:>5} {:>5} {:^30}".format(
                    self.id,
                    self.parentID,
                    self.name + "::" + self.description if len(self.name + "::" + self.description) <= 40 else (
                                                                                                                       self.name + "::" + self.description)[
                                                                                                               :37] + "...",
                    self.numberOfInstances,
                    self.numberOfExternalReferences,
                    self.numberOfComplexes,
                    self.numberOfMacromolecules,
                    u"(" + u", ".join(map(str, map(lambda c: round(c, 3), colour))) + u")",
                )
            return string
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            if self._long:
                string = u"""\
                \r{}
                \rID:\t\t{}
                \rPARENT ID:\t{}
                \rSegment Type:\t{}
                \r{}
                \rName:
                \r\t{}
                \rDescription:
                \r\t{}
                \rNumber of instances:
                \r\t{}
                \r{}
                \rExternal references:
                \r{}
                \r{}
                \rComplexes:
                \r{}
                \rMacromolecules:
                \r{}
                \r{}
                \rColour:
                \r\t{}\
                """.format(
                    # ****
                    self.LINE3,
                    self.id,
                    self.parentID,
                    self.segmentType,
                    # ---
                    self.LINE2,
                    self.name,
                    self.description,
                    self.numberOfInstances,
                    # -----
                    self.LINE2,
                    self.externalReferences,
                    # ----
                    self.LINE2,
                    self.complexes,
                    self.macromolecules,
                    # ----
                    self.LINE2,
                    self.colour,
                )
            elif self.list_ids:
                string = u"{}".format(self.id)
            else:
                colour = self.colour
                string = u"{:<7} {:<7} {:<40} {:>5} {:>5} {:>5} {:>5} {:^30}".format(
                    self.id,
                    self.parentID,
                    self.name + "::" + self.description if len(self.name + "::" + self.description) <= 40 else (
                                                                                                                       self.name + "::" + self.description)[
                                                                                                               :37] + "...",
                    self.numberOfInstances,
                    self.numberOfExternalReferences,
                    self.numberOfComplexes,
                    self.numberOfMacromolecules,
                    u"(" + u", ".join(map(str, map(lambda c: round(c, 3), colour))) + u")",
                )
            return string


class HeaderView(View):
    """HeaverView class
    
    Display EMDB-SFF header
    """

    def __init__(self, segmentation):
        self._segmentation = segmentation

    @property
    def name(self):
        if self._segmentation.name:
            return self._segmentation.name
        else:
            return self.NOT_DEFINED

    @property
    def version(self):
        return self._segmentation.version

    @property
    def software(self):
        if self._segmentation.software.name is not None:
            software_name = self._segmentation.software.name
        else:
            software_name = self.NOT_DEFINED
        if self._segmentation.software.version is not None:
            software_version = self._segmentation.software.version
        else:
            software_version = self.NOT_DEFINED
        if self._segmentation.software.processingDetails is not None:
            software_processing_details = textwrap.fill(
                "\t" + self._segmentation.software.processingDetails,
                self.DISPLAY_WIDTH
            )
        else:
            software_processing_details = u"\t" + self.NOT_DEFINED
        software = u"""\
\tSoftware: {}
\tVersion:  {}
Software processing details: \n{}\
        """.format(
            software_name,
            software_version,
            software_processing_details
        )
        return software

    @property
    def primaryDescriptor(self):
        return self._segmentation.primaryDescriptor

    @property
    def boundingBox(self):
        return self._segmentation.boundingBox.xmin, self._segmentation.boundingBox.xmax, \
               self._segmentation.boundingBox.ymin, self._segmentation.boundingBox.ymax, \
               self._segmentation.boundingBox.zmin, self._segmentation.boundingBox.zmax

    @property
    def globalExternalReferences(self):
        if self._segmentation.globalExternalReferences:
            string_list = list()
            string_list.append(
                u"{:>3} {:<16} {:<56} {:<20} {:1} {:1}".format(
                    "#",
                    "resource",
                    "iri",
                    "short_form",
                    "L",
                    "D",
                )
            )
            string_list.append(u"\t" + u"-" * (self.DISPLAY_WIDTH - len(u"\t".expandtabs())))
            i = 0
            for gExtRef in self._segmentation.globalExternalReferences:
                type_ = gExtRef.type
                otherType = gExtRef.otherType
                value = gExtRef.value
                label = u"Y" if gExtRef.label is not None else u"N"
                description = u"Y" if gExtRef.description is not None else u"N"
                string_list.append(
                    u"\t{id:>2}: {type:<16} {otherType:<56} {value:<20} {label:1} {description:1}".format(
                        id=i,
                        type=type_,
                        otherType=otherType,
                        value=value,
                        label=label,
                        description=description,
                    )
                )
                i += 1
            return "\n".join(string_list)
        else:
            return self.NOT_DEFINED

    @property
    def details(self):
        if self._segmentation.details:
            return u"\n".join(textwrap.wrap(u"\t" + self._segmentation.details, self.DISPLAY_WIDTH))
        else:
            return u"\t" + self.NOT_DEFINED

    if sys.version_info[0] > 2:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            string = u"""\
                    \r{}
                    \rEMDB-SFF v.{}
                    \r{}
                    \rSegmentation name:
                    \r\t{}
                    \rSegmentation software:
                    \r{}
                    \r{}
                    \rPrimary descriptor [threeDVolume|meshList|shapePrimitiveList]:
                    \r\t{}
                    \r{}
                    \rBounding box (xmin,xmax,ymin,ymax,zmin,zmax):
                    \r\t{}
                    \r{}
                    \rGlobal external references:
                    \r\t{}
                    \r{}
                    \rSegmentation details:
                    \r{}\
                    """.format(
                # ===
                self.LINE1,
                self.version,
                # ---
                self.LINE2,
                self.name,
                self.software,
                # ---
                self.LINE2,
                self.primaryDescriptor,
                # ---
                self.LINE2,
                self.boundingBox,
                # ---
                self.LINE2,
                self.globalExternalReferences,
                # ----
                self.LINE2,
                self.details,
            )
            return string
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            string = u"""\
            \r{}
            \rEMDB-SFF v.{}
            \r{}
            \rSegmentation name:
            \r\t{}
            \rSegmentation software:
            \r{}
            \r{}
            \rPrimary descriptor [threeDVolume|meshList|shapePrimitiveList]:
            \r\t{}
            \r{}
            \rBounding box (xmin,xmax,ymin,ymax,zmin,zmax):
            \r\t{}
            \r{}
            \rGlobal external references:
            \r\t{}
            \r{}
            \rSegmentation details:
            \r{}\
            """.format(
                # ===
                self.LINE1,
                self.version,
                # ---
                self.LINE2,
                self.name,
                self.software,
                # ---
                self.LINE2,
                self.primaryDescriptor,
                # ---
                self.LINE2,
                self.boundingBox,
                # ---
                self.LINE2,
                self.globalExternalReferences,
                # ----
                self.LINE2,
                self.details,
            )
            return string


class TableHeaderView(View):
    """Class defining the view of a table header object"""

    if sys.version_info[0] > 2:
        def __bytes__(self):
            return self.__str__().encode('utf-8')

        def __str__(self):
            return self._unicode()
    else:
        def __str__(self):
            return self.__unicode__().encode('utf-8')

        def __unicode__(self):
            return self._unicode()

    def _unicode(self):
        string = u"""\
        \r{}
        \r{:<7} {:<7} {:<40} {:>5} {:>5} {:>5} {:>5} {:^26}
        \r{}\
        """.format(
            View.LINE3,
            u"id",
            u"parId",
            u"name::description",
            u"#inst",
            u"#exRf",
            u"#cplx",
            u"#macr",
            u"colour",
            View.LINE2
        )
        return string


def list_notes(args, configs):
    """List all notes in an EMDB-SFF file
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :return int status: 0 is OK, else failure
    """
    sff_seg = schema.SFFSegmentation(args.sff_file)
    # todo: make this optional
    # todo: define the stream to use
    if args.header:
        string = Styled(u"[[ ''|fg-cyan:no-end ]]")
        string += _str(HeaderView(sff_seg))
        string += Styled(u"[[ ''|reset ]]")
        print(_str(string))
    note_views = [NoteView(segment, _long=args.long_format, list_ids=args.list_ids) for segment in sff_seg.segments]
    if args.sort_by_name:
        sorted_note_views = sorted(note_views, key=lambda n: n.name, reverse=args.reverse)
    else:
        sorted_note_views = sorted(note_views, key=lambda n: n.id, reverse=args.reverse)
    # table header
    if not args.list_ids and not args.long_format:
        string = Styled(u"[[ ''|fg-cyan:no-end ]]")
        string += _str(TableHeaderView())
        string += Styled(u"[[ ''|reset ]]")
        print(_str(string))
    for note_view in sorted_note_views:
        string = Styled(u"[[ ''|fg-cyan:no-end ]]")
        string += _str(note_view)
        string += Styled(u"[[ ''|reset ]]")
        print(_str(string))
    return os.EX_OK


def show_notes(args, configs):
    """Show notes in an EMDB-SFF file for the specified segment IDs
    
    :param args: parsed arguments
    :type args: ``argparse.Namespace``
    :return int status: 0 is OK, else failure
    """
    sff_seg = schema.SFFSegmentation(args.sff_file)
    if args.header:
        string = Styled(u"[[ ''|fg-cyan:no-end ]]")
        string += _str(HeaderView(sff_seg))
        string += Styled(u"[[ ''|reset ]]")
        print(_str(string))
    if args.segment_id is not None:
        if not args.long_format:
            string = Styled(u"[[ ''|fg-cyan:no-end ]]")
            string += _str(TableHeaderView())
            string += Styled(u"[[ ''|reset ]]")
            print(_str(string))
        found_segment = False
        for segment in sff_seg.segments:
            if segment.id in args.segment_id:
                string = Styled(u"[[ ''|fg-cyan:no-end ]]")
                string += _str(NoteView(segment, _long=args.long_format))
                string += Styled(u"[[ ''|reset ]]")
                print(_str(string))
                found_segment = True
        if not found_segment:
            print_date("No segment with ID(s) {}".format(", ".join(map(str, args.segment_id))))
    return os.EX_OK
