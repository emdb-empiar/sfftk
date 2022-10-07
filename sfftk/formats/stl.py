"""
``sfftk.formats.stl``
======================
User-facing reader classes for Stereolithography files
"""
import inspect
import os.path

import numpy
import sfftkrw.schema.adapter_v0_8_0_dev1 as schema
from sfftkrw.core.print_tools import print_date

from .base import Segmentation, Header, Segment, Annotation, Mesh
from ..readers import stlreader

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-11"


class STLMesh(Mesh):
    """Mesh class"""

    def __init__(self, vertices, polygons):
        self._vertices = vertices
        self._polygons = polygons

    @property
    def vertices(self):
        """Vertices in this mesh"""
        return self._vertices

    @property
    def polygons(self):
        """Polygons in this mesh"""
        return self._polygons

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFMesh` object"""
        # convert the dict to a list of 4-tuples where the first item is the key
        indexed_vertices = sorted(((k, v[0], v[1], v[2]) for k, v in self.vertices.items()),
                                  key=lambda v: v[0])
        # validate vertices
        # vertices are valid if len(vertices) == last_index + 1
        # meaning? all vertices from 0 to last_index exist; no holes
        try:
            assert indexed_vertices[0][0] == 0 and len(indexed_vertices) == indexed_vertices[-1][0] + 1
        except AssertionError:
            raise ValueError("missing one or more vertices")
        # validate polygons/triangles
        # now we know that all vertex indexes exist
        _triangles = list(self.polygons.values())
        # create triangles
        triangles = numpy.array(_triangles)
        vertex_ids = set(self.vertices.keys())
        polygon_vertex_ids = set(triangles.flatten().tolist())
        # validate polygons
        # polygons are valid if all vertex IDs exists in the vertices dict
        try:
            assert vertex_ids == polygon_vertex_ids
        except AssertionError:
            raise ValueError(
                "incompatible vertices and triangles due to reference(s) to non-existent vertex/vertices")
        # create vertices
        _vertices = numpy.array(indexed_vertices)
        # indexed vertices had an extra column of the index value; now we delete that column
        vertices = numpy.delete(_vertices, 0, axis=1)
        # now we can create the mesh
        mesh = schema.SFFMesh(
            vertices=schema.SFFVertices.from_array(vertices),
            triangles=schema.SFFTriangles.from_array(triangles)
        )
        return mesh


class STLAnnotation(Annotation):
    """Annotation class"""

    def __init__(self, name):
        self.name = name
        # import random
        # self.colour = tuple([random.random() for _ in _xrange(3)])

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFBiologicalAnnotation` object"""
        annotation = schema.SFFBiologicalAnnotation(
            name=self.name,
        )
        colour = schema.SFFRGBA(random_colour=True)
        return annotation, colour


class STLSegment(Segment):
    """Segment class"""

    def __init__(self, name, vertices, polygons):
        self._name = name
        self._vertices = vertices
        self._polygons = polygons

    @property
    def name(self):
        """Segment name"""
        return self._name

    @property
    def annotation(self):
        """Segmentation annotation"""
        return STLAnnotation(self.name)

    @property
    def meshes(self):
        """Segment meshes"""
        return [STLMesh(self._vertices, self._polygons)]

    def convert(self):
        """Convert to a :py:class:`sfftkrw.SFFSegment` object"""
        segment = schema.SFFSegment()
        segment.biological_annotation, segment.colour = self.annotation.convert()
        meshes = schema.SFFMeshList()
        for mesh in self.meshes:
            meshes.append(mesh.convert())
        segment.mesh_list = meshes
        return segment


class STLHeader(Header):
    """Class definition for header in an STL segmentation file"""

    def __init__(self, segmentation):
        """Initialise an STLHeader object

        :param segmentation: raw segmentation obtained from :py:func:`sfftk.readers.stlreader.get_data` function
        """
        self._segmentation = segmentation

        for attr in dir(self._segmentation):
            if attr[:1] == "_":
                continue
            elif inspect.ismethod(getattr(self._segmentation, attr)):
                continue
            else:
                setattr(self, attr, getattr(self._segmentation, attr))

    def convert(self):
        """Convert to an EMDB-SFF segmentation header

        Currently not implemented"""
        pass


class STLSegmentation(Segmentation):
    """Class representing an STL segmentation

    .. code-block:: python

        from sfftk.formats.stl import STLSegmentation
        stl_seg = STLSegmentation('file.stl')
    """

    def __init__(self, fns, *args, **kwargs):
        self._fns = fns
        self._segments = list()
        for fn in self._fns:
            print_date("{}: Stereolithography mesh".format(os.path.basename(fn)))
            segment = stlreader.get_data(fn, *args, **kwargs)
            for name, vertices, polygons in segment:
                self._segments.append(STLSegment(name, vertices, polygons))

    @property
    def header(self):
        """The header in the segmentation"""
        return STLHeader(self._segments[0])

    @property
    def segments(self):
        """The segments in the segmentation"""
        return self._segments

    def convert(self, name=None, software_version=None, processing_details=None, details=None, verbose=False, transform=None):
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

        segmentation.name = name if name is not None else "STL Segmentation"
        segmentation.software_list = schema.SFFSoftwareList()
        segmentation.software_list.append(
            schema.SFFSoftware(
                name="Unspecified",
                version=software_version if software_version is not None else "Unspecified",
                processing_details=processing_details
            )
        )
        segmentation.transform_list = schema.SFFTransformList()
        if transform is not None:
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix.from_array(transform)
            )
        else:
            # todo: we should convert back to image space because STLs are usually in physical space
            segmentation.transform_list.append(
                schema.SFFTransformationMatrix(
                    rows=3,
                    cols=4,
                    data='1.0 0.0 0.0 1.0 0.0 1.0 0.0 1.0 0.0 0.0 1.0 1.0'
                )
            )
        segmentation.primary_descriptor = "mesh_list"

        segments = schema.SFFSegmentList()
        for s in self.segments:
            segments.append(s.convert())

        segmentation.segment_list = segments
        # details
        segmentation.details = details

        return segmentation
