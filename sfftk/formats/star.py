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
from sfftkrw.schema.adapter_v0_8_0_dev1 import schema

from .base import Segment, Header, Segmentation
from ..readers import starreader


class RelionStarHeader(Header):
    """Class repreenting a Relion STAR file header"""


class RelionStarSegment(Segment):
    """Class representing a Relion STAR file segment"""

    def __init__(self, *args, **kwargs):
        pass


class RelionStarSegmentation(Segmentation):
    """Class that represents a Relion STAR file segmentation"""

    def __init__(self, fn, *args, **kwargs):
        """Initialise the segmentation"""
        self._fn = fn
        self._segmentation = starreader.get_data(self._fn, *args, **kwargs)

    @property
    def header(self, ):
        """Return the header"""
        return RelionStarHeader()

    @property
    def segments(self, ):
        """Return the segments"""
        return [RelionStarSegment()]

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False, transform=None):
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
        segmentation.segments_list = schema.SFFSegmentList()
        # fixme: where do the particles come from
        for particle in self._segmentation.particles:
            transform = schema.SFFTransformationMatrix(
                particle.affine_matrix
            )
            segment = schema.SFFSegment(
                id=particle.particle_id,
                name=f"Particle {particle.particle_id}",
                number_of_instances=1,
                transforms=schema.SFFTransformList(
                    transform
                )
            )
            segmentation.transform_list.append(transform)
            segmentation.segments_list.append(segment)
        # segments: each segment will reference a transform; perhaps we should create the transforms and segments together
        # lattice
        return segmentation
