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
from sfftkrw.core.print_tools import print_date

from .base import Segment, Segmentation
from ..formats import map as mapformat
from ..readers import starreader, mapreader


class RelionStarHeader(mapformat.MaskHeader):
    """Class repreenting a Relion STAR file header"""


class RelionStarSegment(Segment):
    """Class representing a Relion STAR file segment"""

    def __init__(self, particles: starreader.StarTable, euler_angle_convention='ZYZ', degrees=True, verbose=False):
        self._particles = particles
        self._euler_angle_convention = euler_angle_convention
        self._degrees = degrees
        self._verbose = verbose

    def convert(self, **kwargs):
        """Convert the segment to an EMDB-SFF segment"""
        segment = schema.SFFSegment()
        # metadata
        segment.biological_annotation = schema.SFFBiologicalAnnotation()
        segment.biological_annotation.name = "Particle refined using subtomogram averaging"
        segment.colour = schema.SFFRGBA(random_colour=True)
        segment.shape_primitive_list = schema.SFFShapePrimitiveList()
        transforms = schema.SFFTransformList()
        if self._verbose:
            print_date(f"Using Euler angle convention: {self._euler_angle_convention}")
            print_date(f"Euler angles in degrees: {not self._degrees}")
        for id, particle in enumerate(self._particles, start=1):
            transform = schema.SFFTransformationMatrix.from_array(
                particle.to_affine_transform(
                    axes=self._euler_angle_convention,
                    degrees=self._degrees
                ), id=id
            )
            shape = schema.SFFSubtomogramAverage(
                lattice_id=kwargs.get('lattice_id'),
                value=1.0,  # todo: capture the isosurface value e.g. from the CLI,
                transform_id=transform.id,
            )
            segment.shape_primitive_list.append(shape)
            transforms.append(transform)
        return segment, transforms


class RelionStarSegmentation(Segmentation):
    """Class that represents a Relion STAR file segmentation"""

    def __init__(self, fn, particle_fn, euler_angle_convention='ZYZ', degrees=True, *_args, **_kwargs):
        """Initialise the segmentation"""
        self._fn = fn
        self._particle_fn = particle_fn
        self._euler_angle_convention = euler_angle_convention
        self._degrees = degrees
        self._segmentation = starreader.get_data(self._fn, *_args, **_kwargs)
        self._density = mapreader.get_data(self._particle_fn, *_args, **_kwargs)
        self._segments = [
            RelionStarSegment(
                self._segmentation.tables['_rln'],
                euler_angle_convention=self._euler_angle_convention,
                degrees=self._degrees,
                verbose=_kwargs.get('verbose', False)
            )]

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
        segmentation.primary_descriptor = "shape_primitive_list"
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
            _transform = schema.SFFTransformationMatrix.from_array(transform)
            segmentation.transform_list.append(
                _transform
            )
        else:
            _transform = schema.SFFTransformationMatrix.from_array(
                numpy.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], ]))
            segmentation.transform_list.append(
                _transform
            )
        # lattice: we need to know the lattice because we reference it in the segment
        segmentation.lattice_list = schema.SFFLatticeList()
        lattice = schema.SFFLattice(
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
        segmentation.lattice_list.append(lattice)
        segmentation.segment_list = schema.SFFSegmentList()
        for segment in self.segments:
            _segment, _transforms = segment.convert(lattice_id=lattice.id)
            segmentation.segment_list.append(_segment)
            segmentation.transform_list.extend(_transforms)
        segmentation.details = details
        return segmentation
