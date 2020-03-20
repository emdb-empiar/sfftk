#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
``sfftk.notes.view``
=============================

Display notes in EMDB-SFF files
"""
from __future__ import division, print_function

import os
import sys
import textwrap

import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core import _str
from sfftkrw.core.print_tools import print_date
from styled import Styled

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
    def parent_id(self):
        return self._segment.parent_id

    @property
    def name(self):
        if self._segment.biological_annotation.name:
            return self._segment.biological_annotation.name
        else:
            return self.NOT_DEFINED

    @property
    def description(self):
        if self._segment.biological_annotation.description:
            return textwrap.fill(self._segment.biological_annotation.description, self.DISPLAY_WIDTH)
        else:
            return self.NOT_DEFINED

    @property
    def number_of_instances(self):
        if self._segment.biological_annotation.number_of_instances:
            return self._segment.biological_annotation.number_of_instances
        else:
            return self.NOT_DEFINED_ALT

    @property
    def number_of_external_references(self):
        return self._segment.biological_annotation.num_external_references

    @property
    def external_references(self):
        if self._segment.biological_annotation:
            string_list = list()
            string_list.append(
                u"\t{:>3} {:<16} {:<56} {:<20} {:1} {:1}".format(
                    u"#",
                    u"resource",
                    u"url",
                    u"accession",
                    u"L",
                    u"D",
                )
            )
            string_list.append(u"\t" + u"-" * (self.DISPLAY_WIDTH - len(u"\t".expandtabs())))
            i = 0
            for ext_ref in self._segment.biological_annotation.external_references:
                resource = ext_ref.resource
                url = ext_ref.url
                accession = ext_ref.accession
                label = u"Y" if ext_ref.label is not None else u"N"
                description = u"Y" if ext_ref.description is not None else u"N"
                string_list.append(
                    u"\t{id:>2}: {resource:<16} {url:<56} {accession:<20} {label:1} {description:1}".format(
                        id=i,
                        resource=resource,
                        url=url,
                        accession=accession,
                        label=label,
                        description=description,
                    )
                )
                i += 1
            return "\n".join(string_list)
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
        if self._segment.mesh_list:
            segment_type.append(u"mesh_list")
        if self._segment.shape_primitive_list:
            segment_type.append(u"shape_primitive_list")
        if self._segment.three_d_volume:
            segment_type.append(u"three_d_volume")
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
                \rColour:
                \r\t{}\
                """.format(
                    # ****
                    self.LINE3,
                    self.id,
                    self.parent_id,
                    self.segmentType,
                    # ---
                    self.LINE2,
                    self.name,
                    self.description,
                    self.number_of_instances,
                    # -----
                    self.LINE2,
                    self.external_references,
                    # ----
                    # ----
                    self.LINE2,
                    self.colour,
                )
            elif self.list_ids:
                string = u"{}".format(self.id)
            else:
                colour = self.colour
                string = u"{:<7} {:<7} {:<50} {:>5} {:>5} {:^30}".format(
                    self.id,
                    self.parent_id,
                    self.name + "::" + self.description if len(self.name + "::" + self.description) <= 40 else (
                                                                                                                       self.name + "::" + self.description)[
                                                                                                               :37] + "...",
                    self.number_of_instances,
                    self.number_of_external_references,
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
                \rColour:
                \r\t{}\
                """.format(
                    # ****
                    self.LINE3,
                    self.id,
                    self.parent_id,
                    self.segmentType,
                    # ---
                    self.LINE2,
                    self.name,
                    self.description,
                    self.number_of_instances,
                    # -----
                    self.LINE2,
                    self.external_references,
                    # ----
                    self.LINE2,
                    self.colour,
                )
            elif self.list_ids:
                string = u"{}".format(self.id)
            else:
                colour = self.colour
                string = u"{:<7} {:<7} {:<50} {:>5} {:>5} {:^30}".format(
                    self.id,
                    self.parent_id,
                    self.name + "::" + self.description if len(self.name + "::" + self.description) <= 40 else (
                                                                                                                       self.name + "::" + self.description)[
                                                                                                               :37] + "...",
                    self.number_of_instances,
                    self.number_of_external_references,
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
    def software_list(self):
        software = u""
        for i, sw in enumerate(self._segmentation.software_list):
            if sw.name is not None:
                sw_name = sw.name
            else:
                sw_name = u"\t" + self.NOT_DEFINED
            if sw.version is not None:
                sw_version = sw.version
            else:
                sw_version = u"\t" + self.NOT_DEFINED
            if sw.processing_details is not None:
                sw_proc_det = textwrap.fill(u"\tproc/det: " + sw.processing_details, self.DISPLAY_WIDTH)
            else:
                sw_proc_det = u"\tproc/det: " + self.NOT_DEFINED
            software += u"\t{id} {name}/{version}\n{proc_det}\n".format(
                id=i,
                name=sw_name,
                version=sw_version,
                proc_det=sw_proc_det,
            )
        return software

    @property
    def primary_descriptor(self):
        return self._segmentation.primary_descriptor

    @property
    def bounding_box(self):
        if self._segmentation.bounding_box is not None:
            return self._segmentation.bounding_box.xmin, self._segmentation.bounding_box.xmax, \
                   self._segmentation.bounding_box.ymin, self._segmentation.bounding_box.ymax, \
                   self._segmentation.bounding_box.zmin, self._segmentation.bounding_box.zmax

    @property
    def global_external_references(self):
        if self._segmentation.global_external_references:
            string_list = list()
            string_list.append(
                u"{:>3} {:<16} {:<56} {:<20} {:1} {:1}".format(
                    "#",
                    "resource",
                    "url",
                    "accession",
                    "L",
                    "D",
                )
            )
            string_list.append(u"\t" + u"-" * (self.DISPLAY_WIDTH - len(u"\t".expandtabs())))
            i = 0
            for g_ext_ref in self._segmentation.global_external_references:
                resource = g_ext_ref.resource
                url = g_ext_ref.url
                accession = g_ext_ref.accession
                label = u"Y" if g_ext_ref.label is not None else u"N"
                description = u"Y" if g_ext_ref.description is not None else u"N"
                string_list.append(
                    u"\t{id:>2}: {resource:<16} {url:<56} {accession:<20} {label:1} {description:1}".format(
                        id=i,
                        resource=resource,
                        url=url,
                        accession=accession,
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
                    \rPrimary descriptor [three_d_volume|mesh_list|shape_primitive_list]:
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
                self.software_list,
                # ---
                self.LINE2,
                self.primary_descriptor,
                # ---
                self.LINE2,
                self.bounding_box,
                # ---
                self.LINE2,
                self.global_external_references,
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
            \rPrimary descriptor [three_d_volume|mesh_list|shape_primitive_list]:
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
                self.software_list,
                # ---
                self.LINE2,
                self.primary_descriptor,
                # ---
                self.LINE2,
                self.bounding_box,
                # ---
                self.LINE2,
                self.global_external_references,
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
        \r{:<7} {:<7} {:<50} {:>5} {:>5} {:^26}
        \r{}\
        """.format(
            View.LINE3,
            u"id",
            u"par_id",
            u"name::description",
            u"#inst",
            u"#ext_ref",
            u"colour",
            View.LINE2
        )
        return string


def list_notes(args, configs):
    """List all notes in an EMDB-SFF file
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :return status: 0 is OK, else failure
    :rtype status: int
    """
    sff_seg = schema.SFFSegmentation.from_file(args.sff_file)
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
        if args.list_ids:
            string = _str(note_view)
        else:
            # add colour
            string = Styled(u"[[ ''|fg-cyan:no-end ]]")
            string += _str(note_view)
            string += Styled(u"[[ ''|reset ]]")
        print(_str(string))
    return os.EX_OK


def show_notes(args, configs):
    """Show notes in an EMDB-SFF file for the specified segment IDs
    
    :param args: parsed arguments
    :type args: :py:class:`argparse.Namespace`
    :return status: 0 is OK, else failure
    :rtype status: int
    """
    sff_seg = schema.SFFSegmentation.from_file(args.sff_file)
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
        for segment in sff_seg.segment_list:
            if segment.id in args.segment_id:
                string = Styled(u"[[ ''|fg-cyan:no-end ]]")
                string += _str(NoteView(segment, _long=args.long_format))
                string += Styled(u"[[ ''|reset ]]")
                print(_str(string))
                found_segment = True
        if not found_segment:
            print_date("No segment with ID(s) {}".format(", ".join(map(str, args.segment_id))))
            return os.EX_DATAERR
    return os.EX_OK
