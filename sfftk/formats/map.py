# -*- coding: utf-8 -*-
# map.py
"""
``sfftk.formats.map``
=====================

User-facing reader classes for CCP4 masks
"""
from __future__ import division, print_function

import inspect
import os
import sys

import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core import _xrange
from sfftkrw.core.print_tools import print_date, get_printable_ascii_string

from .base import Segmentation, Header, Segment, Annotation
from ..readers import mapreader

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-09"
__updated__ = '2018-02-23'


class MapAnnotation(Annotation):
    """Annotation class"""

    def __init__(self, map_obj):
        self._map_obj = map_obj
        for attr in dir(self._map_obj):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._map_obj, attr)):
                continue
            if attr == "voxels":  # leave the voxels for the volume
                continue
            setattr(self, attr, getattr(self._map_obj, attr))

    @property
    def cols(self):
        return self._nc

    @property
    def rows(self):
        return self._nr

    @property
    def sections(self):
        return self._ns

    @property
    def start_cols(self):
        return self._ncstart

    @property
    def start_rows(self):
        return self._nrstart

    @property
    def start_sections(self):
        return self._nsstart

    @property
    def x_length(self):
        return self._x_length

    @property
    def y_length(self):
        return self._y_length

    @property
    def z_length(self):
        return self._z_length

    @property
    def mode(self):
        if self._mode == 3 or self._mode == 4:
            raise ValueError("Fourier transform instead of segmentation")
        elif 0 <= self._mode <= 2:
            return MODE_STRING[self._mode]

    @property
    def endianness(self):
        if (self._machst[0] == '\x44' and self._machst[1] == '\x41' and self._machst[2] == '\x00' and self._machst[
            3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'D' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00') or \
                (self._machst[0] == 'D' and self._machst[1] == 'A' and self._machst[2] == '\x00' and self._machst[
                    3] == '\x00'):
            return 'little'
        elif self._machst[0] == '\x11' and self._machst[1] == '\x11' and self._machst[2] == '\x00' and self._machst[
            3] == '\x00':
            return 'big'
        else:
            raise ValueError("MACHST = ", self._machst)

    @property
    def name(self):
        """Segment name (filename since we have a segment per file)"""
        return os.path.basename(self._map_obj._fn)

    @property
    def description(self):
        """Segment description (concat all labels)"""
        desc = ''
        for i in _xrange(self._nlabl):
            desc += get_printable_ascii_string(getattr(self, '_label_{}'.format(i)))
        return desc

    @property
    def colour(self):
        """Segment colour"""
        return None

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFBiologicalAnnotation` object"""
        annotation = schema.SFFBiologicalAnnotation()
        annotation.name = self.name
        annotation.number_of_instances = 1
        import random
        red, green, blue = random.random(), random.random(), random.random()
        print_date(
            "Colour not defined for mask segments. Setting colour to random RGB value of {}".format((red, green, blue))
        )
        colour = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
        )
        return annotation, colour


class MapSegment(Segment):
    """Segment class"""

    def __init__(self, map_obj):
        self._map_obj = map_obj

    @property
    def annotation(self):
        """Segment annotation"""
        return MapAnnotation(self._map_obj)

    # @property
    # def volume(self):
    #     """Three-D volume data in this segment"""
    #     return MapVolume(self._map_obj)

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFSegment` object"""
        lattice = schema.SFFLattice(
            mode=self.annotation.mode,
            endianness=self.annotation.endianness,
            size=schema.SFFVolumeStructure(
                cols=self.annotation.cols,
                rows=self.annotation.rows,
                sections=self.annotation.sections,
            ),
            start=schema.SFFVolumeIndex(
                cols=self.annotation.start_cols,
                rows=self.annotation.start_rows,
                sections=self.annotation.start_sections,
            ),
            data=self._map_obj.voxels,
        )
        segment = schema.SFFSegment()
        segment.biological_annotation, segment.colour = self.annotation.convert()
        segment.three_d_volume = schema.SFFThreeDVolume(
            lattice_id=lattice.id,
            value=1.0,
        )
        return segment, lattice


MODE_STRING = {
    0: 'int8',
    1: 'int16',
    2: 'float32',
}


class MapHeader(Header):
    """Class defining the header in a CCP4 file"""

    def __init__(self, segment):
        self._map_obj = segment.annotation._map_obj
        for attr in dir(self._map_obj):
            if attr[:2] == "__":
                continue
            if inspect.ismethod(getattr(self._map_obj, attr)):
                continue
            if attr == "voxels":  # leave the voxels for the volume
                continue
            setattr(self, attr, getattr(self._map_obj, attr))

    @property
    def cols(self):
        return self._nc

    @property
    def rows(self):
        return self._nr

    @property
    def sections(self):
        return self._ns

    @property
    def start_cols(self):
        return self._ncstart

    @property
    def start_rows(self):
        return self._nrstart

    @property
    def start_sections(self):
        return self._nsstart

    @property
    def x_length(self):
        return self._x_length

    @property
    def y_length(self):
        return self._y_length

    @property
    def z_length(self):
        return self._z_length

    @property
    def mode(self):
        if self._mode == 3 or self._mode == 4:
            raise ValueError("Fourier transform instead of segmentation")
        elif 0 <= self._mode <= 2:
            return MODE_STRING[self._mode]


class MapSegmentation(Segmentation):
    """Class representing an CCP4/MAP mask segmentation
    
    .. code-block:: python
    
        from sfftk.formats.map import MapSegmentation
        map_seg = MapSegmentation('file.map')
        
    """

    def __init__(self, fns, *args, **kwargs):
        """Initialise the MapSegmentation reader"""
        self._fns = fns

        # set the segmentation attribute
        self._segments = list()
        cols, rows, sections = 0, 0, 0
        for fi, fn in enumerate(fns):
            self._segments.append(MapSegment(mapreader.get_data(fn, *args, **kwargs)))
            segment_annotation = self._segments[fi].annotation
            if fi == 0:
                cols = segment_annotation.cols
                rows = segment_annotation.rows
                sections = segment_annotation.sections
            else:
                if cols != segment_annotation.cols or rows != segment_annotation.rows or sections != segment_annotation.sections:
                    print_date("{}: CCP4 mask of dimensions: cols={}, rows={}, sections={}".format(
                        os.path.basename(fn), segment_annotation.cols, segment_annotation.rows,
                        segment_annotation.sections)
                    )
                    print_date("Error: The provided CCP4 masks have different volume dimensions")
                    sys.exit(os.EX_DATAERR)
            print_date("{}: CCP4 mask of dimensions: cols={}, rows={}, sections={}".format(
                os.path.basename(fn), cols, rows, sections)
            )

        # self._map_obj = mapreader.get_data(fn)

    """
    :TODO: document attributes and methods of readers
    """

    @property
    def header(self):
        """Segmentation metadata must be exactly as in one segment"""
        return MapHeader(self.segments[0])

    @property
    def segments(self):  # only one segment
        """The segments in this segmentation"""
        return self._segments
        # return [MapSegment(self)]

    def convert(self, args, *_args, **_kwargs):
        """Convert to a :py:class:`sfftkrw.SFFSegmentation` object"""
        segmentation = schema.SFFSegmentation()

        # segmentation.name = self.header.name
        segmentation.name = "CCP4 mask segmentation"

        # software
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="Undefined",
                version="Undefined",
            )
        )
        # segmentation.filePath = os.path.dirname(os.path.abspath(self._fn))
        segmentation.primary_descriptor = "three_d_volume"

        segmentation.bounding_box = schema.SFFBoundingBox(
            xmax=self.header.x_length,
            ymax=self.header.y_length,
            zmax=self.header.z_length,
        )

        # transforms
        segmentation.transform_list = schema.SFFTransformList()

        segmentation.transform_list.append(
            schema.SFFTransformationMatrix.from_array(self.header.ijk_to_xyz_transform)
        )
        segmentation.transform_list.append(
            schema.SFFTransformationMatrix.from_array(self.header.skew_matrix)
        )
        segmentation.transform_list.append(
            schema.SFFTransformationMatrix.from_array(self.header.skew_translation)
        )

        segment_list = schema.SFFSegmentList()
        lattice_list = schema.SFFLatticeList()
        for s in self.segments:
            segment, lattice = s.convert()
            segment_list.append(segment)
            lattice_list.append(lattice)

        # finally pack everything together
        segmentation.segment_list = segment_list
        segmentation.lattice_list = lattice_list

        if args.details is not None:
            segmentation.details = args.details
        elif 'details' in _kwargs:
            segmentation.details = _kwargs['details']
        return segmentation
