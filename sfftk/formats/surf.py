"""
``sfftk.formats.surf``
======================

User-facing reader classes for Amira HxSurface files
"""
import inspect

import numpy
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core import _xrange

from .base import Segmentation, Header, Segment, Annotation, Mesh
from ..readers import surfreader

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-11"


class AmiraHyperSurfaceMesh(Mesh):
    """Mesh class"""

    def __init__(self, segment):
        self._vertices = segment.vertices
        self._triangles = segment.triangles

    @property
    def vertices(self):
        """Dictionary of vertex_id to (x, y, z)"""
        return self._vertices

    @property
    def polygons(self):
        """List of (v1, v2, v3) (triangles)"""
        return self._triangles

    # fixme: consider moving this to the superclass
    @staticmethod
    def translate_indexes(triangle_list, lut):
        """Translate the values of the list of 3-tuples according to the provided look-up table

        Is a generator.

        :param list triangle_list: a list of 3-tuples of integers
        :param dict lut: a dictionary mapping current to new values
        """
        for t0, t1, t2 in triangle_list:
            yield lut[t0], lut[t1], lut[t2]

    def convert(self, **kwargs):
        """Convert to a :py:class:`sfftkrw.SFFMesh` object"""
        indexed_vertices = sorted(((k, v[0], v[1], v[2]) for k, v in self.vertices.items()),
                                  key=lambda v: v[0])
        vertex_keys = sorted(self.vertices.keys())
        # a look-up table to remap indices to start from 0
        # some vertex ids will be missing hence the translation
        lut = dict(zip(vertex_keys, _xrange(len(vertex_keys))))
        _original_triangles = list(self.polygons)
        _triangles = list(self.translate_indexes(_original_triangles, lut))
        triangles = numpy.array(_triangles)
        # create vertices
        # we do not perform validation because by selecting vertices in sequence we impose order
        # furthermore, the translation above guarantees only valid indices exist
        _vertices = numpy.array(indexed_vertices)
        # indexed vertices had an extra column of the index value; now we delete that column
        vertices = numpy.delete(_vertices, 0, axis=1)
        mesh = schema.SFFMesh(
            vertices=schema.SFFVertices.from_array(vertices),
            triangles=schema.SFFTriangles.from_array(triangles)
        )
        return mesh


class AmiraHyperSurfaceAnnotation(Annotation):
    """Annotation class"""

    def __init__(self, segment):
        self._segment = segment
        self._name = segment[0].name
        self._colour = segment[0].colour

    @property
    def name(self):
        """Segment name"""
        return self._name

    @property
    def colour(self):
        """Segment colour"""
        return self._colour

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFBiologicalAnnotation` object"""
        # annotation
        annotation = schema.SFFBiologicalAnnotation(
            name=self.name,
            description=self.name,
            number_of_instances=1,
        )
        # colour
        red, green, blue = self.colour
        colour = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
        )
        return annotation, colour


class AmiraHyperSurfaceSegment(Segment):
    """Segment class"""

    def __init__(self, segment):
        self._segment = segment
        self._segment_id = segment[0].id
        self._annotation = AmiraHyperSurfaceAnnotation(segment)
        # meshes
        self._meshes = [AmiraHyperSurfaceMesh(s) for s in self._segment]

    @property
    def id(self):
        """Segment ID"""
        return self._segment_id

    @property
    def annotation(self):
        """Segment annotation"""
        return self._annotation

    @property
    def meshes(self):
        """Segment meshes"""
        return self._meshes

    def convert(self, **kwargs):
        """Convert to a :py:class:`sfftkrw.SFFSegment` object"""
        segment = schema.SFFSegment()
        segment.biological_annotation, segment.colour = self.annotation.convert()
        meshes = schema.SFFMeshList()
        for i, mesh in enumerate(self.meshes):
            meshes.append(mesh.convert())
        segment.mesh_list = meshes
        return segment


class AmiraHyperSurfaceHeader(Header):
    """Class definition for an AmiraHyperSurface segmentation file"""

    def __init__(self, header):
        """Initialise an ``AmiraHyperSurfaceHeader`` object

        :param header: the raw header obtained as a ``ahds.header.AmiraHeader`` object
        """
        self._header = header
        # for attr in dir(self._header):
        #     if attr[:2] == "__" or attr[:1] == "_":
        #         continue
        #     elif inspect.ismethod(getattr(self._header, attr)):
        #         continue
        #     else:
        #         setattr(self, attr, getattr(self._header, attr))
        for attr in header.attrs():
            if inspect.ismethod(getattr(header, attr)):
                continue
            else:
                setattr(self, attr, getattr(header, attr))

    def convert(self):
        """Convert to an EMDB-SFF segmentation header object

        Currently not implemented
        """
        pass


class AmiraHyperSurfaceSegmentation(Segmentation):
    """Class representing an AmiraHyperSurface segmentation

    .. code-block:: python

        from sfftk.formats.surf import AmiraHyperSurfaceSegmentation
        surf_seg = AmiraHyperSurfaceSegmentation('file.surf')
    """

    def __init__(self, fn):
        self._fn = fn
        header, segments = surfreader.get_data(self._fn)
        self._header = AmiraHyperSurfaceHeader(header)
        self._segments = list()
        for segment_id, segment in segments.items():
            self._segments.append(AmiraHyperSurfaceSegment(segment))

    @property
    def header(self):
        """The header in the segmentation"""
        return self._header

    @property
    def segments(self):
        """The segments in the segmentation"""
        return self._segments

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False,
                transform=None):
        """Convert to a :py:class:`sfftkrw.SFFSegmentation` object

        :param str name: optional name of the segmentation used in <name/>
        :param str software_version: optional software version for Amira use in <software><version/></software>
        :param str processing_details: optional processings used in Amira used in <software><processingDetails/></software>
        :param str details: optional details associated with this segmentation used in <details/>
        :param bool verbose: option to determine whether conversion should be verbose
        :param transform: a 3x4 numpy.ndarray for the image-to-physical space transform
        :type transform: `numpy.ndarray`
        """
        segmentation = schema.SFFSegmentation()
        segmentation.name = name if name is not None else "Amira HyperSurface Segmentation"
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="Amira",
                version=software_version if software_version is not None else self.header.version,
                processing_details=processing_details
            )
        )
        # transforms
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
        segmentation.primary_descriptor = "mesh_list"
        # segments
        segmentation.segment_list = schema.SFFSegmentList()
        for i, s in enumerate(self.segments):
            segmentation.segment_list.append(s.convert())
        # details
        segmentation.details = details
        return segmentation
