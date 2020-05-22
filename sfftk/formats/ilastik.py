# -*- coding: utf-8 -*-
"""
``sfftk.formats.ilastik``
=====================

User-facing reader classes for ilastik segmentation files

"""
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from ..readers import ilastikreader


class IlastikHeader(object):
    """Header"""

class IlastikSegment(object):
    """Segment"""

class IlastikSegmentation(object):
    """Class representating an ilastik segmentation"""
    def __init__(self, fn, *args, **kwargs):
        self._fn = fn
        self._segmentation = ilastikreader.get_data(self._fn, *args, **kwargs)

    @property
    def header(self):
        return IlastikHeader(self._segmentation)

    @property
    def segments(self):
        return iter(IlastikSegment(self._segmentation, segment_id) for segment_id in self._segmentation.segment_ids)

    def convert(self, args, *_args, **_kwargs):
        segmentation = schema.SFFSegmentation()
        segmentation.name = u"ilastik Segmentation"
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="ilastik",
                version="v1.3.3post3",
                processing_details="Autocontext (2-stage)",
            )
        )
        segmentation.transform_list = schema.SFFTransformList()
        segmentation.transform_list.append(
            # schema.SFFTransformationMatrix.
        )
        segmentation.primary_descriptor = "three_d_volume"
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segments.append(s.convert(args, *_args, **_kwargs))
        segmentation.segment_list = segments
        # lattice
        segmentation.lattice_list = schema.SFFLatticeList()
        segmentation.lattice_list.append(
            schema.SFFLattice(
                mode='uint8',
            )
        )
