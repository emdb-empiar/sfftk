# -*- coding: utf-8 -*-
# surf.py
'''
sfftk.formats.surf
===================

User-facing reader classes for Amira HxSurface files
'''
from __future__ import division

import inspect
import os.path

from .. import schema
from ..readers import surfreader
from .base import Segmentation, Header, Segment, Annotation, Mesh

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-11"
__updated__ = '2018-02-23'


class AmiraHyperSurfaceMesh(Mesh):
    '''Mesh class'''
    def __init__(self, segment):
        self._vertices = segment.vertices
        self._triangles = segment.triangles
    @property
    def vertices(self):
        '''Dictionary of vertex_id to (x, y, z)'''
        return self._vertices
    @property
    def polygons(self):
        '''List of (v1, v2, v3) (triangles)'''
        return self._triangles
    def convert(self):
        '''Convert to a :py:class:`sfftk.schema.SFFMesh` object'''
        #  vertices
        vertices = schema.SFFVertexList()
        for vID, v in self.vertices.iteritems():
            x, y, z = v
            vertex = schema.SFFVertex(
                vID=vID,
                x=x, y=y, z=z
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
    '''Annotation class'''
    def __init__(self, segment):
        self._segment = segment
        self._name = self._segment.name
        self._colour = self._segment.colour
    @property
    def name(self):
        '''Segment name'''
        return self._name
    @property
    def colour(self):
        '''Segment colour'''
        return self._colour
    def convert(self):
        '''Convert to a :py:class:`sfftk.schema.SFFBiologicalAnnotation` object'''
        # annotation
        annotation = schema.SFFBiologicalAnnotation(
            description=self.name,
            numberOfInstances=1,
            )
        # colour
        red, green, blue = self.colour
        colour = schema.SFFColour()
        colour.rgba = schema.SFFRGBA(
                red=red,
                green=green,
                blue=blue,
                )
        return annotation, colour


class AmiraHyperSurfaceSegment(Segment):
    '''Segment class'''
    def __init__(self, segment):
        self._segment = segment
        self._segment_id = self._segment.id
        self._annotation = AmiraHyperSurfaceAnnotation(segment)
        # meshes
        self._meshes = [AmiraHyperSurfaceMesh(segment)]
    @property
    def id(self):
        '''Segment ID'''
        return self._segment_id
    @property
    def annotation(self):
        '''Segment annotation'''
        return self._annotation
    @property
    def meshes(self):
        '''Segment meshes'''
        return self._meshes
    def convert(self, *args, **kwargs):
        '''Convert to a :py:class:`sfftk.schema.SFFSegment` object'''
        segment = schema.SFFSegment()
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        meshes = schema.SFFMeshList()
        for mesh in self.meshes:
            meshes.add_mesh(mesh.convert())
        segment.meshes = meshes
        return segment


class AmiraHyperSurfaceHeader(Header):
    '''Header class'''
    def __init__(self, header):
        self._header = header
        for attr in dir(self._header):
            if attr[:2] == "__" or attr[:1] == "_":
                continue
            elif inspect.ismethod(getattr(self._header, attr)):
                continue
            else:
                setattr(self, attr, getattr(self._header, attr))

    def convert(self):
        pass


class AmiraHyperSurfaceSegmentation(Segmentation):
    '''Class representing an AmiraHyperSurface segmentation
    
    .. code:: python
    
        from sfftk.formats.surf import AmiraHyperSurfaceSegmentation
        surf_seg = AmiraHyperSurfaceSegmentation('file.surf')
        
    '''
    def __init__(self, fn):
        self._fn = fn
        header, segments = surfreader.get_data(self._fn)
        self._header = AmiraHyperSurfaceHeader(header)
        self._segments = list()
        for segment in segments.itervalues():
            self._segments.append(AmiraHyperSurfaceSegment(segment))
    @property
    def header(self):
        '''The header in the segmentation'''
        return self._header
    @property
    def segments(self):
        '''The segments in the segmentation'''
        return self._segments
    def convert(self, args, *_args, **_kwargs):
        '''Convert to a :py:class:`sfftk.schema.SFFSegmentation` object'''
        segmentation = schema.SFFSegmentation()
        segmentation.name = "Amira HyperSurface Segmentation"
        segmentation.software = schema.SFFSoftware(
            name="Amira",
            version=self.header.designation.version,
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
