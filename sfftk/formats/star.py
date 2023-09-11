"""
Working with STAR files

STAR files are CIF files.
To use STAR files with sfftk, the user needs to provide at least:
- a STAR file
- a map file (MRC, REC, MAP, CCP4, etc.)

.. code-block:: bash

    sff convert --relion-star <starfile> <mrcfile> -o <outputfile> [other options]

The presence of the --star flag tells sfftk that what is about to be generated is a refinement model plus transforms.


"""
import numpy
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema

from .base import Segment, Segmentation
from ..formats import map as mapformat
from ..readers import starreader, mapreader


class RelionStarHeader(mapformat.MaskHeader):
    """Class repreenting a Relion STAR file header"""


class RelionStarSegment(Segment):
    """Class representing a Relion STAR file segment"""

    def __init__(self, particle: starreader.StarTableRow, *args, **kwargs):
        self._particle = particle

    @property
    def transformation_matrix(self):
        """Return the transformation matrix"""
        return self._particle.to_affine_transform()

    def convert(self, **kwargs):
        """Convert the segment to an EMDB-SFF segment"""
        segment = schema.SFFSegment()
        # transform
        transform = schema.SFFTransformationMatrix.from_array(self.transformation_matrix)
        # metadata
        segment.biological_annotation = schema.SFFBiologicalAnnotation()
        segment.biological_annotation.name = f"Particle #{segment.id}"
        segment.three_d_volume = schema.SFFThreeDVolume(
            lattice_id=0,
            value=1.0,
            transform_id=transform.id
        )
        return segment, transform


class RelionStarSegmentation(Segmentation):
    """Class that represents a Relion STAR file segmentation"""

    def __init__(self, fn, particle_fn, *args, **kwargs):
        """Initialise the segmentation"""
        self._fn = fn
        self._particle_fn = particle_fn
        self._segmentation = starreader.get_data(self._fn, *args, **kwargs)
        self._density = mapreader.get_data(self._particle_fn, *args, **kwargs)
        self._segments = [RelionStarSegment(particle) for particle in self._segmentation.tables['_rln']]

    @property
    def header(self, ):
        """Return the header"""
        return RelionStarHeader(self._density)

    @property
    def segments(self):
        """Return the segments"""
        return self._segments

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False,
                transform=None):
        """Convert the segmentation to an EMDB-SFF segmentation"""
        segmentation = schema.SFFSegmentation()
        # metadata
        segmentation.name = name if name is not None else "RELION Subtomogram Average"
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name='RELION',
                version=software_version if software_version is not None else 'v4.0',
                processing_details=processing_details
            )
        )
        segmentation.details = details
        # transforms
        segmentation.transform_list = schema.SFFTransformList()
        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(
                    numpy.array([
                        [1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                    ])
                )
            )
        # now load the particles
        segmentation.segment_list = schema.SFFSegmentList()
        segment_colour = schema.SFFRGBA(random_colour=True)  # one colour for all segments
        for segment in self.segments:
            _segment, _transform = segment.convert()
            _segment.colour = segment_colour
            segmentation.transform_list.append(_transform)
            segmentation.segment_list.append(_segment)
        # lattice
        segmentation.lattice_list = schema.SFFLatticeList()
        segmentation.lattice_list.append(
            schema.SFFLattice(
                mode=self.header.mode,
                endinaness=self.header.endianness,
                size=schema.SFFVolumeStructure(
                    cols=self.header.cols,
                    rows=self.header.rows,
                    sections=self.header.sections
                ),
                start=schema.SFFVolumeIndex(
                    cols=self.header.start_cols,
                    rows=self.header.start_rows,
                    sections=self.header.start_sections
                ),
                data=self._density.voxels
            )
        )
        return segmentation
