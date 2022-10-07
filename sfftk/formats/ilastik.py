"""
``sfftk.formats.ilastik``
=====================

User-facing reader classes for ilastik segmentation files

"""
import numpy
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core import _str

from ..readers import ilastikreader


class IlastikHeader:
    def __init__(self, segmentation):
        self._segmentation = segmentation


class IlastikSegment(object):
    """Segment"""

    def __init__(self, segmentation, segment_id):
        self._segmentation = segmentation
        self._segment_id = segment_id

    def convert(self, **kwargs):
        segment = schema.SFFSegment(id=self._segment_id)
        segment.biological_annotation = schema.SFFBiologicalAnnotation()
        segment.biological_annotation.name = "ilastik segment #{id}".format(id=self._segment_id)
        segment.colour = schema.SFFRGBA(random_colour=True)
        segment.three_d_volume = schema.SFFThreeDVolume(
            value=self._segment_id,
            lattice_id=0,
        )
        return segment


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

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False, transform=None):
        """
        Convert to a :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else "ilastik Segmentation"
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="ilastik",
                version=software_version if software_version is not None else "Unspecified",
                processing_details=processing_details,
            )
        )
        segmentation.transform_list = schema.SFFTransformList()
        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(
                    numpy.array([
                        [1.0, 0.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0, 0.0],
                    ], dtype=float)
                )
            )
        segmentation.primary_descriptor = "three_d_volume"
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segments.append(s.convert())
        segmentation.segment_list = segments
        # lattice
        segmentation.lattice_list = schema.SFFLatticeList()
        sections, rows, cols = self._segmentation.shape
        segmentation.lattice_list.append(
            schema.SFFLattice(
                mode=_str(self._segmentation.dtype),
                size=schema.SFFVolumeStructure(cols=cols, rows=rows, sections=sections),
                start=schema.SFFVolumeIndex(cols=0, rows=0, sections=0),
                data=self._segmentation.data,
            )
        )
        # details
        segmentation.details = details
        return segmentation
