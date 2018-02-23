#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
sfftk.formats.seg
=================

User-facing reader classes for Segger files

'''
from __future__ import division

from .. import schema
from ..readers import segreader
from .base import Annotation, Volume, Segment, Header, \
    Segmentation

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2017-02-02"
__updated__ = '2018-02-23'


class SeggerAnnotation(Annotation):
    '''Annotation class'''
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
        '''Convert to a :py:class:`sfftk.schema.SFFBiologicalAnnotation` object'''
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
    '''Volume class'''
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
        '''Convert to a :py:class:`sfftk.schema.SFFThreeDVolume` object'''
        volume = schema.SFFThreeDVolume()
        volume.file = self.file
        volume.contourLevel = self.map_level
        volume.transformId = 1
        volume.format = "Segger"
        return volume


class SeggerSegment(Segment):
    '''Segment class'''
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
        '''Convert to a :py:class:`sfftk.schema.SFFSegment` object'''
        segment = schema.SFFSegment()
        segment.id = self.region_id
        segment.parentID = self.parent_id
        # annotation
        segment.annotation, segment.colour = self.annotation.convert()
        # geometry
        segment.volume = self.volume.convert()
        return segment


class SeggerHeader(Header):
    '''Header class'''
    def __init__(self, segmentation):
        self._segmentation = segmentation
    @property
    def name(self):
        '''The name of segmentation'''
        return self._segmentation.format
    @property
    def version(self):
        '''The version of Segger used'''
        return self._segmentation.format_version
    @property
    def map_path(self):
        '''The path to the original segmented map'''
        return self._segmentation.map_path
    @property
    def ijk_to_xyz_transform(self):
        '''The image-to-physical transform'''
        return self._segmentation.ijk_to_xyz_transform
    @property
    def file_path(self):
        '''The path to the .seg file'''
        return self._segmentation.file_path
    @property
    def root_parent_ids(self):
        '''Parent IDs for root segments'''
        return self._segmentation.root_parent_ids
    @property
    def region_ids(self):
        '''All region IDs'''
        return self._segmentation.region_ids
    @property
    def parent_ids(self):
        '''All parent IDs'''
        return self._segmentation.parent_ids


class SeggerSegmentation(Segmentation):
    '''Class representing an Segger segmentation
    
    .. code:: python
    
        from sfftk.formats.seg import SeggerSegmentation
        seg_seg = SeggerSegmentation('file.seg')
        
    '''
    def __init__(self, fn, top_level=False, *args, **kwargs):
        '''Initialise the reader'''
        self._fn = fn
        self._segmentation = segreader.get_data(self._fn, *args, **kwargs)
        self._top_level = top_level
    @property
    def header(self):
        '''The header for this segmentation'''
        return SeggerHeader(self._segmentation)
    @property
    def segments(self):
        '''The segments in this segmentation'''
        if self._top_level:
            segments = [SeggerSegment(self._segmentation, region_id) for region_id in self.header.root_parent_ids]
        else:
            segments = [SeggerSegment(self._segmentation, region_id) for region_id in self.header.region_ids if region_id != 0]
        return segments
    def convert(self, args, *_args, **_kwargs):
        '''Method to convert a :py:class:`sfftk.schema.SFFSegmentation` object'''
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
        if args.details is not None:
            segmentation.details = args.details
        elif 'details' in _kwargs:
            segmentation.details = _kwargs['details']
        return segmentation

