# -*- coding: utf-8 -*-
# surf.py
"""
sfftk.formats.surf
===================

User-facing reader classes for Amira HxSurface files
"""
from __future__ import division, print_function

import inspect

import os.path

from .base import Segmentation, Header, Segment, Annotation, Mesh
from .. import schema
from ..readers import surfreader
from ..core import _dict_iter_items

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

    def convert(self):
        """Convert to a :py:class:`sfftk.schema.SFFMesh` object"""
        #  vertices
        vertices = schema.SFFVertexList()
        for vID, v in _dict_iter_items(self.vertices):
            x, y, z = v
            vertex = schema.SFFVertex(
                vID=vID,
                x=x, y=y, z=z,
            )
            vertices.add_vertex(vertex)
        # polygons
        polygons = schema.SFFPolygonList()
        for P in self.polygons:
            polygon = schema.SFFPolygon()
            v1, v2, v3 = P
            polygon.add_vertex(v1)
            polygon.add_vertex(v2)
            polygon.add_vertex(v3)
            polygons.add_polygon(polygon)
        # finally...
        mesh = schema.SFFMesh()
        mesh.vertices = vertices
        mesh.polygons = polygons
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
        """Convert to a :py:class:`sfftk.schema.SFFBiologicalAnnotation` object"""
        # annotation
        annotation = schema.SFFBiologicalAnnotation(
            name=self.name,
            description=self.name,
            numberOfInstances=1,
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

    def convert(self, *args, **kwargs):
        """Convert to a :py:class:`sfftk.schema.SFFSegment` object"""
        segment = schema.SFFSegment()
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        meshes = schema.SFFMeshList()
        for mesh in self.meshes:
            meshes.add_mesh(mesh.convert())
        segment.meshes = meshes
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
    
    .. code:: python
    
        from sfftk.formats.surf import AmiraHyperSurfaceSegmentation
        surf_seg = AmiraHyperSurfaceSegmentation('file.surf')
        
    """

    def __init__(self, fn):
        self._fn = fn
        header, segments = surfreader.get_data(self._fn)
        self._header = AmiraHyperSurfaceHeader(header)
        self._segments = list()
        for segment_id, segment in _dict_iter_items(segments):
            self._segments.append(AmiraHyperSurfaceSegment(segment))

    @property
    def header(self):
        """The header in the segmentation"""
        return self._header

    @property
    def segments(self):
        """The segments in the segmentation"""
        return self._segments

    def convert(self, args, *_args, **_kwargs):
        """Convert to a :py:class:`sfftk.schema.SFFSegmentation` object"""
        segmentation = schema.SFFSegmentation()
        segmentation.name = "Amira HyperSurface Segmentation"
        segmentation.software = schema.SFFSoftware(
            name="Amira",
            version=self.header.version,
        )
        # transforms
        segmentation.transforms = schema.SFFTransformList()
        segmentation.transforms.add_transform(
            schema.SFFTransformationMatrix(
                rows=3,
                cols=4,
                data='1.0 0.0 0.0 1.0 0.0 1.0 0.0 1.0 0.0 0.0 1.0 1.0'
            )
        )
        segmentation.filePath = os.path.abspath(self._fn)
        segmentation.primaryDescriptor = "meshList"
        # segments
        segments = schema.SFFSegmentList()
        for s in self.segments:
            segments.add_segment(s.convert())
        segmentation.segments = segments
        # details
        if args.details is not None:
            segmentation.details = args.details
        elif 'details' in _kwargs:
            segmentation.details = _kwargs['details']
        return segmentation
