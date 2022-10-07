"""
``sfftk.formats.am``
====================

User-facing reader classes for AmiraMesh files

"""
import inspect
import os.path

import numpy
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core.print_tools import print_date

from .base import Segmentation, Segment, Annotation
from ..readers import amreader

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-10"
__updated__ = '2018-02-23'

"""
:TODO: handle meshes <hxsurface>
"""


class AmiraMeshMesh(object):
    """Mesh class"""

    def __init__(self):
        self._vertices = None
        self._triangles = None

    @property
    def vertices(self):
        """Vertices in mesh"""
        return self._vertices

    @property
    def triangles(self):
        """Triangles in mesh"""
        return self._triangles

    def convert(self, **kwargs):
        """Convert to :py:class:`sfftkrw.SFFMesh` object"""
        mesh = schema.SFFMesh()
        vertices = schema.SFFVertexList()
        polygons = schema.SFFPolygonList()
        mesh.vertices = vertices
        mesh.polygons = polygons
        return mesh


class AmiraMeshAnnotation(Annotation):
    """Annotation class"""

    def __init__(self, material):
        self._material = material

    @property
    def name(self):
        """Segment name"""
        try:
            return self._material.name
        except AttributeError:
            return None

    @property
    def description(self):
        """Segment description"""
        try:
            return self._material.name
        except AttributeError:
            return None

    @property
    def colour(self):
        """Segment colour

        Colour may or may not exist. Return None if it doesn't and the caller will determine what to do"""
        try:
            colour = self._material.Color
        except AttributeError:
            colour = None
        return colour

    def convert(self, **kwargs):
        """Convert to :py:class:`sfftkrw.SFFBiologicalAnnotation` object"""
        annotation = schema.SFFBiologicalAnnotation()
        annotation.name = self.name
        annotation.description = self.description
        annotation.number_of_instances = 1
        if self.colour:
            red, green, blue = self.colour
        else:
            import random
            red, green, blue = random.random(), random.random(), random.random()
            print_date("Colour not defined for segment (Material) {}. Setting colour to random RGB value of {}".format(
                self.description, (red, green, blue)))
        colour = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
        )
        return annotation, colour


class AmiraMeshVolume(object):
    """Class defining the 3D volume of an AmiraMesh segmentation file

    :param str fn: name of the AmiraMesh segmentation file
    :param header: :py:class:`AmiraMeshHeader` object
    """

    def __init__(self, fn, header):
        self._fn = fn
        self._header = header

    def convert(self, **kwargs):
        """Convert to :py:class:`sfftkrw.SFFThreeDVolume` object"""
        volume = schema.SFFThreeDVolume()
        # make file
        hdf5_fn = "".join(self._fn.split('.')[:-1]) + '.hdf'
        volume.file = os.path.basename(hdf5_fn)
        volume.format = "Segger"
        return volume


class AmiraMeshSegment(Segment):
    """Segment class"""

    def __init__(self, fn, header, segment_id):
        """Initialiser of AmiraMeshSegment

        :param header: an ``AmiraMeshHeader`` object containing header metadata
        :type header: AmiraMeshHeader
        :param int segment_id: the integer identifier for this segment ('Id' in Materials)
        """
        self._fn = fn
        self._header = header
        self._segment_id = segment_id

    @property
    def segment_id(self):
        return self._segment_id

    @property
    def material(self):
        """Material may or may not exist. Return None if it doesn't and the caller will determine what to do"""
        try:  # assume that we have materials defined
            material = self._header.Parameters.Materials[
                self.segment_id]  # Ids are 1-based but in the images are 0-based
        except AttributeError:
            material = None
        except IndexError:
            material = None
        return material

    @property
    def annotation(self):
        """Segment annotation"""
        return AmiraMeshAnnotation(self.material)

    @property
    def volume(self):
        """The segmentation as a volume"""
        return AmiraMeshVolume(self._fn, self._header)

    def convert(self, **kwargs):
        """Convert to :py:class:`sfftkrw.SFFSegment` object"""
        segment = schema.SFFSegment()
        segment.biological_annotation, segment.colour = self.annotation.convert()
        segment.three_d_volume = schema.SFFThreeDVolume(
            lattice_id=0,
            value=self.segment_id,
        )
        return segment


class AmiraMeshHeader(object):
    """Class defining the header of an AmiraMesh segmentation file"""

    def __init__(self, header):
        """Initialise an AmiraMeshHeader object

        Adds attributes from the ``ahda.header.AmiraHeader`` object into this one

        :param header: header from an AmiraMesh segmentation file
        :type header: ``ahda.header.AmiraHeader`` object
        """
        self._header = header

        for attr in header.attrs():
            if inspect.ismethod(getattr(header, attr)):
                continue
            else:
                setattr(self, attr, getattr(header, attr))

    def convert(self, **kwargs):
        """Convert an AmiraMeshHeader object into an EMDB-SFF segmentation header

        Currently empty"""
        pass


class AmiraMeshSegmentation(Segmentation):
    """Class representing an AmiraMesh segmentation

    .. code-block:: python

        from sfftk.formats.am import AmiraMeshSegmentation
        am_seg = AmiraMeshSegmentation('file.am')
    """

    def __init__(self, fn, *args, **kwargs):
        self._fn = fn
        _header, self._volume = amreader.get_data(self._fn, *args, **kwargs)
        self._header = AmiraMeshHeader(_header)
        self._segments = list()
        indices_set = set(numpy.unique(self._volume.data))
        segment_indices = indices_set.difference({0})  # do not include '0' as a label
        for segment_id in segment_indices:
            self._segments.append(AmiraMeshSegment(self._fn, self.header, segment_id))

    @property
    def header(self):
        """The AmiraMesh header obtained using the :py:mod:`ahds` package

        The header is wrapped with a generic :py:mod:`ahds.header` class
        """
        return self._header

    @property
    def segments(self):
        """Segments in this segmentation"""
        return self._segments

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False, transform=None):
        """Convert to :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else "AmiraMesh Segmentation"
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="Amira",
                version=software_version if software_version is not None else "Unspecified",
                processing_details=processing_details
            )
        )
        segmentation.transform_list = schema.SFFTransformList()
        # fixme: use proper values for image-to-physical transform
        segmentation.primary_descriptor = "three_d_volume"
        if self.header.Parameters.BoundingBox:
            x0, x1, y0, y1, z0, z1 = self.header.Parameters.BoundingBox
            segmentation.bounding_box = schema.SFFBoundingBox(
                xmin=x0, xmax=x1,
                ymin=y0, ymax=y1,
                zmin=z0, zmax=z1,
            )
            c, r, s = self.header.Lattice.length
            # compute the image-to-physical transform from the bounding box and image size
            arr = numpy.array(
                [[(x1 - x0) / c, 0.0, 0.0, 0.0],
                 [0.0, (y1 - y0) / r, 0.0, 0.0],
                 [0.0, 0.0, (z1 - z0) / s, 0.0]]
            )
            segmentation.transform_list.append(schema.SFFTransformationMatrix.from_array(arr))
        elif transform is not None:
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

        segments = schema.SFFSegmentList()
        for s in self.segments:
            segment = s.convert()
        segments.append(segment)

        # finally pack everything together
        segmentation.segment_list = segments
        # """
        # lattices
        lattices = schema.SFFLatticeList()
        # the lattice
        cols, rows, sections = self._volume.shape[::-1]
        if verbose:
            print_date('creating lattice...')
        lattice = schema.SFFLattice(
            mode='uint8',
            endianness='little',
            size=schema.SFFVolumeStructure(cols=cols, rows=rows, sections=sections),
            start=schema.SFFVolumeIndex(cols=0, rows=0, sections=0),
            data=self._volume.data,  # the numpy data is on the .data attribute
        )
        if verbose:
            print_date('adding lattice...')
        lattices.append(lattice)
        segmentation.lattice_list = lattices
        segmentation.details = details
        return segmentation
