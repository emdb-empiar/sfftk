#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sfftk.formats.seg


"""

from __future__ import division

import sys
from .. import schema
from base import Annotation, Volume, Segment, Header, \
    Segmentation
from ..readers import segreader


__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-02-02"


class SeggerAnnotation(Annotation):
    def __init__(self, segmentation, region_id):
        self._segmentation = segmentation
        self._region_id = region_id
    @property
    def description(self):
        return ''
    @property
    def colour(self):
        r, g, b, a = self._segmentation.region_colours[self._region_id]
        return r, g, b, a
    def convert(self, *args, **kwargs):
        annotation = schema.SFFBiologicalAnnotation()
        annotation.description = self.description
        annotation.numberOfInstances = 1
        colour = schema.SFFColour()
        r, g, b, a = self.colour
        colour.rgba = schema.SFFRGBA(
            red=r,
            green=g,
            blue=b,
            alpha=a,
            )
        return annotation, colour


class SeggerVolume(Volume):
    def __init__(self, segmentation):
        self._segmentation = segmentation
    @property
    def file(self):
        return self._segmentation.file_name
    @property
    def map_level(self):
        return self._segmentation.map_level
    @property
    def mask(self):
        return self._segmentation.mask
    def convert(self):
        volume = schema.SFFThreeDVolume()
        volume.file = self.file
        volume.contourLevel = self.map_level
        volume.transformId = 1
        volume.format = "Segger"
        return volume


class SeggerSegment(Segment):
    def __init__(self, segmentation, region_id):
        self._segmentation = segmentation
        self._region_id = region_id
    @property
    def annotation(self):
        return SeggerAnnotation(self._segmentation, self.region_id)
    @property
    def region_id(self):
        return self._region_id
    @property
    def parent_id(self):
        return self._segmentation.get_parent_id(self.region_id)
    @property
    def volume(self):
        return SeggerVolume(self._segmentation)
    def convert(self, *args, **kwargs):
        segment = schema.SFFSegment()
        segment.id = self.region_id
        segment.parentID = self.parent_id
        # annotation
        segment.annotation, segment.colour = self.annotation.convert()
        # geometry
        segment.volume = self.volume.convert()
        return segment


class SeggerHeader(Header):
    def __init__(self, segmentation):
        self._segmentation = segmentation
    @property
    def name(self):
        return self._segmentation.format
    @property
    def version(self):
        return self._segmentation.format_version
    @property
    def map_path(self):
        return self._segmentation.map_path
    @property
    def ijk_to_xyz_transform(self):
        return self._segmentation.ijk_to_xyz_transform
    @property
    def file_path(self):
        return self._segmentation.file_path
    @property
    def root_parent_ids(self):
        return self._segmentation.root_parent_ids
    @property
    def region_ids(self):
        return self._segmentation.region_ids
    @property
    def parent_ids(self):
        return self._segmentation.parent_ids


class SeggerSegmentation(Segmentation):
    """SeggerReader"""
    def __init__(self, fn, top_level=False, *args, **kwargs):
        """Initialise the reader"""
        self._fn = fn
        self._segmentation = segreader.get_data(self._fn, *args, **kwargs)
        self._top_level = top_level
    @property
    def header(self):
        return SeggerHeader(self._segmentation)
    @property
    def segments(self):
        if self._top_level:
            segments = [SeggerSegment(self._segmentation, region_id) for region_id in self.header.root_parent_ids]
        else:
            segments = [SeggerSegment(self._segmentation, region_id) for region_id in self.header.region_ids if region_id != 0]
        return segments
    def convert(self, *args, **kwargs):
        """Method to convert a Segger file to an EMDB-SFF file"""
        segmentation = schema.SFFSegmentation()
        segmentation.name = "Segger Segmentation"
        segmentation.software = schema.SFFSoftware(
            name=self.header.name,
            version=self.header.version,
            )
        segmentation.transforms = schema.SFFTransformList()
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data='1.0 0.0 0.0 1.0 0.0 1.0 0.0 1.0 0.0 0.0 1.0 1.0'
                )
            )
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data=" ".join(map(str, self.header.ijk_to_xyz_transform.flatten().tolist()))
                )
            )
        segmentation.filePath = self.header.file_path
        segmentation.primaryDescriptor = "threeDVolume"
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segment = s.convert()
            segments.add_segment(segment)
        # finally pack everything together
        segmentation.segments = segments
        # details
        if 'details' in kwargs:
            segmentation.details = kwargs['details']
        return segmentation
        
        