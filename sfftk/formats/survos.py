"""
``sfftk.formats.survos``
========================
"""
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core.print_tools import print_date

from .base import Segmentation, Segment
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

    def convert(self, name=None, colour=None):
        """Convert to a :py:class:`sfftkrw.SFFSegment` object"""
        segment = schema.SFFSegment()
        segment.segment_id = self.segment_id
        segment.biological_annotation = schema.SFFBiologicalAnnotation(
            name=name if name is not None else "SuRVoS Segment #{}".format(self.segment_id)
        )
        segment.colour = colour if colour is not None else schema.SFFRGBA(random_colour=True)
        print_date(
            "Colour not defined for SuRVoS segments. Setting colour to random RGBA value of {}".format(segment.colour))
        segment.three_d_volume = schema.SFFThreeDVolume(
            lattice_id=0,
            value=self.segment_id,
        )
        return segment


class SuRVoSSegmentation(Segmentation):
    """SuRVoS segmentation adapter

    .. code-block:: python

        from sfftk.formats.survos import SuRVoSSegmentation
        am_seg = SuRVoSSegmentation('predictions.h5')
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

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False,
                transform=None):
        """Convert to :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        # header
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else "SuRVoS Segmentation"
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="SuRVoS",
                version=software_version if software_version is not None else "1.0",
                processing_details=processing_details
            )
        )
        segmentation.transform_list = schema.SFFTransformList()
        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix(
                    rows=3,
                    cols=4,
                    data='1.0 0.0 0.0 1.0 0.0 1.0 0.0 1.0 0.0 0.0 1.0 1.0'
                )
            )
        segmentation.primary_descriptor = "three_d_volume"
        # segments
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segment = s.convert()
            segments.append(segment)
        segmentation.segment_list = segments
        # lattices
        lattices = schema.SFFLatticeList()
        # the lattice
        sections, rows, cols = self._segmentation.data.shape
        # there is only one lattice
        lattice = schema.SFFLattice(
            mode='int8',  # we make it as small as practically possible; filled values are negative
            endianness='little',
            size=schema.SFFVolumeStructure(cols=cols, rows=rows, sections=sections),
            start=schema.SFFVolumeIndex(cols=0, rows=0, sections=0),
            data=self._segmentation.data,  # the numpy data is on the .data attribute
        )
        lattices.append(lattice)
        segmentation.lattice_list = lattices
        segmentation.details = details
        return segmentation
