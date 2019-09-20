# -*- coding: utf-8 -*-
from __future__ import print_function

from .base import Segmentation, Segment
from .. import schema
from ..core.print_tools import print_date
from ..readers import survosreader


class SuRVoSSegment(Segment):
    """A single SuRVoS segment"""

    def __init__(self, segment_id, segmentation):
        self._segment_id = segment_id
        self._segmentation = segmentation

    @property
    def segment_id(self):
        """As usual, segment IDs start from 1 (not 0)"""
        return self._segment_id + 1

    def convert(self, *args, **kwargs):
        """Convert to a :py:class:`sfftk.schema.SFFSegment` object"""
        segment = schema.SFFSegment()
        segment.segment_id = self.segment_id
        segment.biologicalAnnotation = schema.SFFBiologicalAnnotation(
            name="SuRVoS Segment #{}".format(self.segment_id)
        )
        segment.colour = schema.SFFRGBA(random_colour=True)
        print_date(
            "Colour not defined for SuRVoS segments. Setting colour to random RGBA value of {}".format(segment.colour))
        segment.volume = schema.SFFThreeDVolume(
            latticeId=0,
            value=self.segment_id,
        )

        return segment


class SuRVoSSegmentation(Segmentation):
    """SuRVoS segmentation adapter

    .. code:: python

        from sfftk.formats.survos import SuRVoSSegmentation
        am_seg = SuRVoSSegmentation('predictions.am')
    """

    def __init__(self, fn, *args, **kwargs):
        self._fn = fn
        self._segmentation = survosreader.get_data(fn, *args, **kwargs)
        self._segments = [SuRVoSSegment(segment_id, self._segmentation) for segment_id in
                          self._segmentation.segment_ids()]

    @property
    def segments(self):
        """A list of segments"""
        return self._segments

    def convert(self, args, *_args, **_kwargs):
        """Convert to :py:class:`sfftk.schema.SFFSegmentation` object"""
        # header
        segmentation = schema.SFFSegmentation()
        segmentation.name = "SuRVoS Segmentation"
        segmentation.software = schema.SFFSoftware(
            name="SuRVoS",
            version="1.0",
        )
        segmentation.transforms = schema.SFFTransformList()
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data='1.0 0.0 0.0 1.0 0.0 1.0 0.0 1.0 0.0 0.0 1.0 1.0'
            )
        )
        segmentation.primaryDescriptor = "threeDVolume"
        # segments
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segment = s.convert()
            segments.add_segment(segment)
        segmentation.segments = segments
        # lattices
        lattices = schema.SFFLatticeList()
        # the lattice
        sections, rows, cols = self._segmentation.data.shape
        # there is only one lattice
        lattice = schema.SFFLattice(
            mode='int8',  # we make it as small as practically possible; filled values are negative
            endianness='little',
            size=schema.SFFVolumeStructure(cols=cols, rows=rows, sections=sections),
            start=schema.SFFVolumeIndex(cols=0, rows=0, sections=sections),
            data=self._segmentation.data,  # the numpy data is on the .data attribute
        )
        lattices.add_lattice(lattice)
        segmentation.lattices = lattices
        if args.details is not None:
            segmentation.details = args.details
        elif 'details' in _kwargs:
            segmentation.details = _kwargs['details']
        return segmentation
