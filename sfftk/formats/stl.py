# -*- coding: utf-8 -*-
# surf.py
'''
sfftk.formats.stl
==================
User-facing reader classes for Stereolithography files
'''
from __future__ import division

import inspect
import os.path

from .. import schema
from ..readers import stlreader
from .base import Segmentation, Header, Segment, Annotation, Mesh

__author__ = "Paul K. Korir, PhD"
__email__ = "pkorir@ebi.ac.uk, paul.korir@gmail.com"
__date__ = "2016-11-11"
__updated__ = '2018-02-23'


class STLMesh(Mesh):
    '''Mesh class'''
    def __init__(self, vertices, polygons):
        self._vertices = vertices
        self._polygons = polygons
    @property
    def vertices(self):
        '''Vertices in this mesh'''
        return self._vertices
    @property
    def polygons(self):
        '''Polygons in this mesh'''
        return self._polygons
    def convert(self):
        '''Convert to a :py:class:`sfftk.schema.SFFMesh` object'''
        schema.SFFMesh.reset_id()
        mesh = schema.SFFMesh()
        # polygon
        polygons = schema.SFFPolygonList()
        schema.SFFPolygon.reset_id()
        for P in self.polygons.itervalues():
            polygon = schema.SFFPolygon()

            v1, v2, v3 = P
            polygon.add_vertex(v1)
            polygon.add_vertex(v2)
            polygon.add_vertex(v3)

            polygons.add_polygon(polygon)
        # vertices
        vertices = schema.SFFVertexList()
        for vertex_id, v in self.vertices.iteritems():
            x, y, z = v
            vertex = schema.SFFVertex(vID=vertex_id, x=x, y=y, z=z)
            vertices.add_vertex(vertex)
        # final tying
        mesh.vertices = vertices
        mesh.polygons = polygons
        return mesh


class STLAnnotation(Annotation):
    '''Annotation class'''
    def __init__(self, name):
        self.name = name
        import random
        self.colour = tuple([random.random() for _ in xrange(3)])
    def convert(self):
        '''Convert to a :py:class:`sfftk.schema.SFFBiologicalAnnotation` object'''
        annotation = schema.SFFBiologicalAnnotation()
        annotation.description = self.name
        annotation.numberOfInstances = 1

        red, green, blue = self.colour
        colour = schema.SFFColour()
        colour.rgba = schema.SFFRGBA(
            red=red,
            green=green,
            blue=blue,
            )
        return annotation, colour


class STLSegment(Segment):
    '''Segment class'''
    def __init__(self, name, vertices, polygons):
        self._name = name
        self._vertices = vertices
        self._polygons = polygons
    @property
    def name(self):
        '''Segment name'''
        return self._name
    @property
    def annotation(self):
        '''Segmentation annotation'''
        return STLAnnotation(self.name)
    @property
    def meshes(self):
        '''Segment meshes'''
        return [STLMesh(self._vertices, self._polygons)]
    def convert(self):
        '''Convert to a :py:class:`sfftk.schema.SFFSegment` object'''
        segment = schema.SFFSegment()
        segment.biologicalAnnotation, segment.colour = self.annotation.convert()
        meshes = schema.SFFMeshList()
        for mesh in self.meshes:
            meshes.add_mesh(mesh.convert())
        segment.meshes = meshes
        return segment


class STLHeader(Header):
    '''Header class'''
    def __init__(self, segmentation):
        self._segmentation = segmentation

        for attr in dir(self._segmentation):
            if attr[:1] == "_":
                continue
            elif inspect.ismethod(getattr(self._segmentation, attr)):
                continue
            else:
                setattr(self, attr, getattr(self._segmentation, attr))

    def convert(self):
        pass


class STLSegmentation(Segmentation):
    '''Class representing an STL segmentation
    
    .. code:: python
    
        from sfftk.formats.stl import STLSegmentation
        stl_seg = STLSegmentation('file.stl')
        
    '''
    def __init__(self, fn):
        self._fn = fn
        self._segmentation = stlreader.get_data(self._fn)
        self._segments = [STLSegment(name, vertices, polygons) for name, vertices, polygons in self._segmentation]
    @property
    def header(self):
        '''The header in the segmentation'''
        return STLHeader(self._segmentation)
    @property
    def segments(self):
        '''The segments in the segmentation'''
        return self._segments
    def convert(self, args, *_args, **_kwargs):
        '''Convert to a :py:class:`sfftk.schema.SFFSegmentation` object'''
        segmentation = schema.SFFSegmentation()

        segmentation.name = "STL Segmentation"
        segmentation.software = schema.SFFSoftware(
            name="Unknown",
            version="Unknown",
            )
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
